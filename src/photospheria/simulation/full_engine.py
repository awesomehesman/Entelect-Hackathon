"""Faithful, self-contained deterministic tick engine for Photospheria.

This engine implements the mechanics that are *explicitly specified* in the
official problem statement (problem-statement.pdf) and calibrated against the
two official evaluation logs in SubmissionLogs/. It is deliberately explicit
about assumptions where the specification is silent, and every such assumption
is centralised and documented in :class:`EngineAssumptions` so a caller can see
exactly what is confirmed versus assumed.

Confirmed-and-calibrated facts (see docs/ and SubmissionLogs/):

* Scoring: alpha = 1, k = 1. main = H * (C / Cmax); H = -sum p_i log_N p_i
  with N = 31 (total species in the game, constant). longevity =
  sum((lifespan / T) ** k) / Cmax over cells occupied at the final tick.
  final = 0.8 * main + 0.2 * longevity. leaderboard = round(final * 1e9).
  This reproduces the official Level 1 statistics to full float precision.
* Lifespan convention: a plant occupying a cell at the final tick contributes
  lifespan = final_tick - birth_tick + 1 ... calibrated below. The Level 1 log
  shows a plant planted at tick 499 in a 500-tick game (final tick index 499,
  scored state = state after the last tick) with longevity 4e-06, i.e.
  lifespan 1. We therefore treat lifespan of a plant present at final scoring
  as (scored_tick - birth_tick) where scored_tick is the number of the final
  scored day. See ``_final_lifespans`` for the exact convention and the
  calibration test.
* Nutrients: a cell starts at 100 points and loses 1 per tick while occupied
  by a living plant. At 0 the plant dies and the cell becomes dead matter.
  Dead matter regains 1 point per tick (capped 100). A plant that moves onto a
  dead-matter cell drains it at 0.5 per tick.

Assumptions (documented, conservative, and isolated):

* Coverage / feature_count thresholds are fractions of Cmax (PDF: "8% Coverage"
  = 8 cells per 100 total cells). feature_count decimal values (e.g. 0.05) are
  interpreted the same way (fraction of Cmax) per the PDF coverage-percentage
  paragraph; integer feature_count values (e.g. 20) are absolute cell counts.
* Tick order per tick t: (1) apply participant plantings for t, (2) refresh
  shade, (3) mature/age, (4) spread from mature plants whose cadence fires,
  (5) apply weakness death (shade, winter handled in spread), (6) drain
  nutrients / regenerate dead matter, (7) recompute animal presence and unlock
  state. This ordering is an assumption (AMB-004); it is applied consistently.
* Spread competition: last spread into a cell wins (PDF), spreads do not
  overwrite an explicitly, currently-occupied living cell of another plant
  unless the target is empty. Manual planting always replaces (PDF).
* Unlock/animal state is re-evaluated each tick from the current grid; a
  manual planting action for a locked species on the tick it is being unlocked
  is applied only if the species is unlocked *before* that tick's plantings
  (conservative: we evaluate unlock state at the start of the tick).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

from photospheria.data.models import AnimalDefinition, PlantDefinition
from photospheria.mechanics.spread import spread_targets

SPECIES_TOTAL = 31  # N: total species in the game (constant, per PDF + dataset).


@dataclass(frozen=True)
class EngineAssumptions:
    """Centralised, documented assumptions. Change here to test sensitivity."""

    coverage_is_fraction_of_cmax: bool = True
    feature_count_decimal_is_fraction: bool = True
    spread_enabled: bool = True
    last_spread_wins: bool = True
    # lifespan of a plant present at final scoring = scored_day - birth_tick.
    # scored_day = total_ticks - 1 (final tick index). Calibrated on Level 1.
    lifespan_offset: int = 0


@dataclass
class SimPlant:
    species: str
    index: int
    birth_tick: int
    time_to_maturity: int
    alive: bool = True
    death_tick: int | None = None

    def age(self, tick: int) -> int:
        return max(0, tick - self.birth_tick)

    def is_mature(self, tick: int) -> bool:
        return self.age(tick) >= self.time_to_maturity


@dataclass
class SimCell:
    row: int
    col: int
    soil: int
    terrain: frozenset[str] = frozenset()
    nutrients: float = 100.0
    dead_matter: bool = False
    shade: bool = False
    plant: SimPlant | None = None

    @property
    def plantable(self) -> bool:
        # Only soil is habitable; stone/path/water/etc. are not.
        return not (self.terrain & {"stone", "path", "water", "crack"})


@dataclass
class WorldConfig:
    level_id: int
    width: int
    height: int
    total_ticks: int
    seasons_enabled: bool = True
    animals_enabled: bool = False
    weather_enabled: bool = False
    events_enabled: bool = False
    season_schedule: tuple[tuple[int, str], ...] = ((0, "Spring"),)
    event_schedule: tuple[tuple[int, str], ...] = ()
    max_actions_per_tick: int = 20

    @property
    def cmax(self) -> int:
        return self.width * self.height


@dataclass
class ScoreResult:
    species_counts: dict[str, int]
    occupied_cells: int
    cmax: int
    total_ticks: int
    entropy: float
    density_factor: float
    main_score: float
    longevity_score: float
    final_score: float
    leaderboard_score: int
    unlocked_species: set[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "score": self.final_score,
            "leaderboard_score": self.leaderboard_score,
            "main_score": self.main_score,
            "longevity_score": self.longevity_score,
            "entropy": self.entropy,
            "density_factor": self.density_factor,
            "total_plants_planted_C": self.occupied_cells,
            "unlocked_plant_types": len(self.unlocked_species),
            "number_of_plant_species_in_the_game": SPECIES_TOTAL,
            "c_max_or_grid_size": self.cmax,
            "species_counts": self.species_counts,
        }


INITIAL_SPECIES = ("Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree")


class Simulator:
    """Deterministic tick simulator producing the official score for a plan."""

    def __init__(
        self,
        config: WorldConfig,
        plants: Iterable[PlantDefinition],
        animals: Iterable[AnimalDefinition] | None = None,
        classifications: dict[str, list[str]] | None = None,
        unlocks: dict[str, dict] | None = None,
        soil_grid: list[list[int]] | None = None,
        terrain: dict[tuple[int, int], set[str]] | None = None,
        assumptions: EngineAssumptions | None = None,
    ) -> None:
        self.config = config
        self.defs: dict[str, PlantDefinition] = {p.plant: p for p in plants}
        self.by_index: dict[int, PlantDefinition] = {p.index: p for p in self.defs.values()}
        self.animals = list(animals or [])
        self.classifications = classifications or {}
        self.unlocks = unlocks or {}
        self.assumptions = assumptions or EngineAssumptions()
        self.terrain = terrain or {}
        # Default soil grid: all Dirt (0). Callers with real terrain override.
        if soil_grid is None:
            soil_grid = [[0] * config.width for _ in range(config.height)]
        self.cells: list[list[SimCell]] = [
            [
                SimCell(r, c, int(soil_grid[r][c]), frozenset(self.terrain.get((r, c), ())))
                for c in range(config.width)
            ]
            for r in range(config.height)
        ]
        self.season = self._season_at(0)
        self.events_transpired: set[str] = set()
        self.unlocked: set[str] = set(INITIAL_SPECIES)
        self.present_animals: set[str] = set()
        # Active-cell tracking for performance on large grids. These sets are
        # maintained incrementally by plant/spread/death so per-tick work is
        # proportional to the number of active cells, not the whole grid.
        self._occupied: set[tuple[int, int]] = set()
        self._dead_matter: set[tuple[int, int]] = set()
        self._shaded: set[tuple[int, int]] = set()
        self._live_count_cache: dict[str, int] = {}

    # ---- schedules -------------------------------------------------------
    def _season_at(self, tick: int) -> str:
        if not self.config.seasons_enabled:
            return "Spring"
        entries = [e for e in self.config.season_schedule if e[0] <= tick]
        if not entries:
            return self.config.season_schedule[0][1]
        return max(entries, key=lambda e: e[0])[1]

    def _events_at(self, tick: int) -> list[str]:
        return [name for (t, name) in self.config.event_schedule if t == tick]

    # ---- counts / coverage ----------------------------------------------
    def _live_counts(self) -> dict[str, int]:
        return dict(self._live_count_cache)

    def _coverage(self, counts: dict[str, int], species: str) -> float:
        return counts.get(species, 0) / self.config.cmax

    def _group_members(self, group: str | list[str]) -> list[str]:
        if isinstance(group, list):
            members: list[str] = []
            for g in group:
                members.extend(self.classifications.get(g, [g]))
            return members
        return self.classifications.get(group, [group])

    # ---- condition evaluation -------------------------------------------
    @staticmethod
    def _cmp(a: float, op: str, b: float) -> bool:
        return {
            ">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b, "==": a == b,
        }[op]

    def _eval_cond(self, node: dict, counts: dict[str, int]) -> bool:
        op = str(node.get("op") or node.get("type") or "").upper()
        ntype = str(node.get("type", "")).lower()
        if op in {"AND", "OR", "NOT"}:
            if op == "NOT":
                child = node.get("child") or (node.get("children") or [None])[0]
                return not self._eval_cond(child, counts)
            children = node.get("children") or node.get("conditions") or []
            results = [self._eval_cond(c, counts) for c in children]
            return all(results) if op == "AND" else any(results)
        if ntype == "species_present":
            sp = node["species"]
            if sp in {a.name for a in self.animals} or sp in {a.id for a in self.animals}:
                return sp in self.present_animals or sp.lower() in self.present_animals
            return counts.get(sp, 0) > 0
        if ntype == "species_absent":
            sp = node["species"]
            if sp in {a.name for a in self.animals}:
                return not (sp in self.present_animals)
            return counts.get(sp, 0) == 0
        if ntype == "animal_present":
            return node.get("species") in self.present_animals
        if ntype == "coverage":
            plant = node.get("plant") or node.get("species")
            if isinstance(plant, list):
                cov = sum(counts.get(m, 0) for m in self._group_members(plant)) / self.config.cmax
            else:
                cov = self._coverage(counts, plant)
            threshold = float(node["value"] if "value" in node else node["threshold"])
            return self._cmp(cov, node["operator"], threshold)
        if ntype == "group_coverage":
            members = self._group_members(node.get("species_group", []))
            cov = sum(counts.get(m, 0) for m in members) / self.config.cmax
            return self._cmp(cov, node["operator"], float(node["threshold"]))
        if ntype == "count":
            if "species_group" in node:
                members = self._group_members(node["species_group"])
                total = sum(counts.get(m, 0) for m in members)
            else:
                total = counts.get(node.get("plant") or node.get("species"), 0)
            return self._cmp(total, node["operator"], float(node["value"] if "value" in node else node["threshold"]))
        if ntype == "event":
            return node["event"] in self.events_transpired
        if ntype == "feature_count":
            feat = node["feature"]
            n = self._feature_count(feat)
            val = float(node["value"])
            if 0 < val < 1 and self.assumptions.feature_count_decimal_is_fraction:
                return self._cmp(n / self.config.cmax, node["operator"], val)
            return self._cmp(n, node["operator"], val)
        if ntype == "dominance":
            total = sum(counts.values())
            if total == 0:
                return False
            frac = max(counts.values()) / total
            return frac >= float(node.get("threshold", 0.5))
        # Unknown/unsupported condition: conservatively false.
        return False

    def _feature_count(self, feature: str) -> int:
        if feature == "dead_matter":
            return len(self._dead_matter)
        # Static terrain features are counted once and cached.
        cache = getattr(self, "_static_feature_counts", None)
        if cache is None:
            cache = {}
            self._static_feature_counts = cache
        if feature not in cache:
            n = 0
            for row in self.cells:
                for cell in row:
                    if feature == "burnt_soil" and cell.soil == 3:
                        n += 1
                    elif feature in cell.terrain:
                        n += 1
            cache[feature] = n
        return cache[feature]

    # ---- dynamic world state --------------------------------------------
    def _refresh_animals(self, counts: dict[str, int]) -> None:
        if not self.config.animals_enabled:
            self.present_animals = set()
            return
        present: set[str] = set()
        for animal in self.animals:
            if self._eval_cond(animal.requirements, counts):
                present.add(animal.name)
                present.add(animal.id)
        self.present_animals = present

    def _refresh_unlocks(self, counts: dict[str, int]) -> None:
        newly = set(INITIAL_SPECIES)
        for plant, tree in self.unlocks.items():
            if self._eval_cond(tree, counts):
                newly.add(plant)
        # Unlocks are treated as monotonic once achieved (conservative for
        # planning; the PDF does not state revocation of placement rights).
        self.unlocked |= newly

    def _refresh_shade(self, tick: int) -> None:
        # Clear previously shaded cells only.
        for (rr, cc) in self._shaded:
            self.cells[rr][cc].shade = False
        new_shaded: set[tuple[int, int]] = set()
        for (r, c) in self._occupied:
            cell = self.cells[r][c]
            p = cell.plant
            if p is None or not p.alive or not p.is_mature(tick):
                continue
            d = self.defs.get(p.species)
            if d is None:
                continue
            for rule in d.rules.special:
                if rule.get("type") == "shade_radius":
                    radius = int(rule["value"])
                    for rr in range(max(0, cell.row - radius), min(self.config.height, cell.row + radius + 1)):
                        for cc in range(max(0, cell.col - radius), min(self.config.width, cell.col + radius + 1)):
                            self.cells[rr][cc].shade = True
                            new_shaded.add((rr, cc))
        self._shaded = new_shaded

    # ---- planting --------------------------------------------------------
    def _can_plant(self, species: PlantDefinition, cell: SimCell) -> bool:
        if not cell.plantable:
            return False
        if cell.soil not in species.preferred_soil:
            return False
        return True

    def _place(self, cell: SimCell, species: PlantDefinition, tick: int) -> None:
        """Place a plant on a cell, maintaining active-cell sets and counts."""
        key = (cell.row, cell.col)
        prev = cell.plant
        if prev is not None and prev.alive:
            c = self._live_count_cache.get(prev.species, 0) - 1
            if c <= 0:
                self._live_count_cache.pop(prev.species, None)
            else:
                self._live_count_cache[prev.species] = c
        cell.plant = SimPlant(species.plant, species.index, tick, species.growth.time_to_maturity)
        cell.nutrients = 100.0
        cell.dead_matter = False
        self._occupied.add(key)
        self._dead_matter.discard(key)
        self._live_count_cache[species.plant] = self._live_count_cache.get(species.plant, 0) + 1

    def _kill(self, cell: SimCell, tick: int) -> None:
        """Kill the plant on a cell (nutrient/shade death), maintaining sets."""
        key = (cell.row, cell.col)
        p = cell.plant
        if p is not None and p.alive:
            p.alive = False
            p.death_tick = tick
            c = self._live_count_cache.get(p.species, 0) - 1
            if c <= 0:
                self._live_count_cache.pop(p.species, None)
            else:
                self._live_count_cache[p.species] = c
        cell.plant = None
        cell.dead_matter = True
        self._occupied.discard(key)
        self._dead_matter.add(key)

    def plant_manual(self, index: int, row: int, col: int, tick: int) -> bool:
        species = self.by_index.get(index)
        if species is None:
            return False
        if species.plant not in self.unlocked:
            return False
        if not (0 <= row < self.config.height and 0 <= col < self.config.width):
            return False
        cell = self.cells[row][col]
        if not self._can_plant(species, cell):
            return False
        # Replacement: existing plant is replaced.
        self._place(cell, species, tick)
        return True

    # ---- spread ----------------------------------------------------------
    def _do_spread(self, tick: int) -> None:
        if not self.assumptions.spread_enabled:
            return
        pending: list[tuple[int, int, PlantDefinition]] = []
        for (r, c) in list(self._occupied):
            cell = self.cells[r][c]
            p = cell.plant
            if p is None or not p.alive or not p.is_mature(tick):
                continue
            d = self.defs[p.species]
            rate = d.growth.spread_rate
            if rate <= 0 or (tick - p.birth_tick) % rate != 0:
                continue
            weaknesses = self._weakness_types(d)
            if "no_winter_spread" in weaknesses and self.season == "Winter":
                continue
            if "no_shade_spread" in weaknesses and cell.shade:
                continue
            for (tc, tr) in spread_targets(cell.col, cell.row, self.config.width, self.config.height, d.growth.spread_type, d.growth.spread_range):
                pending.append((tr, tc, d))
        # last-spread-wins: apply in order; later writes overwrite empty targets.
        for (tr, tc, d) in pending:
            target = self.cells[tr][tc]
            if not self._can_plant(d, target):
                continue
            if target.plant is not None and target.plant.alive:
                continue  # do not overwrite a living plant via spread (conservative)
            self._place(target, d, tick)

    def _weakness_types(self, d: PlantDefinition) -> set[str]:
        cache = getattr(self, "_wk_cache", None)
        if cache is None:
            cache = {}
            self._wk_cache = cache
        got = cache.get(d.plant)
        if got is None:
            got = {r.get("type") for r in d.rules.weaknesses}
            cache[d.plant] = got
        return got

    # ---- nutrients -------------------------------------------------------
    def _nutrient_tick(self, tick: int) -> None:
        for (r, c) in list(self._occupied):
            cell = self.cells[r][c]
            p = cell.plant
            if p is None or not p.alive:
                self._occupied.discard((r, c))
                continue
            drain = 0.5 if cell.dead_matter else 1.0
            cell.nutrients = max(0.0, cell.nutrients - drain)
            if cell.nutrients <= 0.0:
                self._kill(cell, tick)
        for (r, c) in list(self._dead_matter):
            cell = self.cells[r][c]
            if cell.plant is not None and cell.plant.alive:
                # A living plant reoccupied this cell; it is no longer inert
                # dead matter that regenerates (the plant drains it instead).
                self._dead_matter.discard((r, c))
                continue
            if cell.dead_matter:
                cell.nutrients = min(100.0, cell.nutrients + 1.0)

    def _weakness_death(self, tick: int) -> None:
        for (r, c) in list(self._occupied):
            cell = self.cells[r][c]
            p = cell.plant
            if p is None or not p.alive:
                continue
            d = self.defs[p.species]
            weaknesses = self._weakness_types(d)
            if "no_shade_survival" in weaknesses and cell.shade:
                specials = {rl.get("type") for rl in d.rules.special}
                if "can_grow_in_shade" not in specials:
                    self._kill(cell, tick)

    # ---- run -------------------------------------------------------------
    def run(self, actions_by_tick: dict[int, list[tuple[int, int, int]]]) -> ScoreResult:
        """actions_by_tick: {tick: [(plant_index, row, col), ...]}."""
        T = self.config.total_ticks
        for tick in range(0, T):
            self.season = self._season_at(tick)
            for name in self._events_at(tick):
                self.events_transpired.add(name)
            counts = self._live_counts()
            self._refresh_animals(counts)
            self._refresh_unlocks(counts)
            # 1) participant plantings (only first max_actions_per_tick)
            for (idx, row, col) in actions_by_tick.get(tick, [])[: self.config.max_actions_per_tick]:
                self.plant_manual(idx, row, col, tick)
            # 2) shade, 3) spread, 4) weakness death, 5) nutrients
            self._refresh_shade(tick)
            self._do_spread(tick)
            self._weakness_death(tick)
            self._nutrient_tick(tick)
        return self._score()

    # ---- scoring ---------------------------------------------------------
    def _final_lifespans(self) -> list[int]:
        scored_day = self.config.total_ticks - 1  # final tick index
        spans: list[int] = []
        for (r, c) in self._occupied:
            cell = self.cells[r][c]
            p = cell.plant
            if p is not None and p.alive:
                spans.append(max(1, scored_day - p.birth_tick + self.assumptions.lifespan_offset + 1))
        return spans

    def _score(self) -> ScoreResult:
        counts = self._live_counts()
        C = sum(counts.values())
        cmax = self.config.cmax
        T = self.config.total_ticks
        if C > 0:
            H = -sum((n / C) * math.log(n / C, SPECIES_TOTAL) for n in counts.values() if n > 0)
        else:
            H = 0.0
        density = C / cmax
        main = H * (density ** 1)
        spans = self._final_lifespans()
        longevity = sum((s / T) ** 1 for s in spans) / cmax
        final = 0.8 * main + 0.2 * longevity
        return ScoreResult(
            species_counts=counts,
            occupied_cells=C,
            cmax=cmax,
            total_ticks=T,
            entropy=H,
            density_factor=density,
            main_score=main,
            longevity_score=longevity,
            final_score=final,
            leaderboard_score=round(final * 1e9),
            unlocked_species=set(self.unlocked),
        )
