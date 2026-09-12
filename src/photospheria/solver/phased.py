"""Two-phase solver: unlock via early seeding, then balanced survival-window fill.

Phase 1 (unlock): seed the initial species early so their spread builds the
coverage / counts that trigger animals, which in turn unlock further species.
Unlock state is monotonic once achieved (conservative planning assumption).

Phase 2 (diverse fill): during the survival window (last ~100 ticks), plant a
*balanced* set of every species unlocked by then, in shade-aware zones, so the
final state is both diverse (high entropy) and long-lived.

Because the real terrain is hidden, this solver simulates its own plan on an
assumed all-soil world only to *decide* which species become reachable and to
schedule placements; the resulting action list degrades gracefully on the real
world (rejected placements simply reduce coverage). The guaranteed-reachable
core (the five initial species) is always planted, so the plan can never score
zero the way a terrain-specific coordinate list can.

Deterministic for fixed inputs.
"""

from __future__ import annotations

from dataclasses import dataclass

from photospheria.data.models import PlantDefinition
from photospheria.simulation.full_engine import (
    INITIAL_SPECIES,
    EngineAssumptions,
    Simulator,
    WorldConfig,
)
from photospheria.solver.balanced_fill import order_species_for_shade, survival_window


@dataclass(frozen=True)
class PhasedPlan:
    actions_by_tick: dict[int, list[tuple[int, int, int]]]
    unlocked_at_window: list[str]
    survival_window: tuple[int, int]

    def total_actions(self) -> int:
        return sum(len(v) for v in self.actions_by_tick.values())


def _seed_zone_cells(rows: range, width: int):
    for r in rows:
        for c in range(width):
            yield (r, c)


def build_phased_plan(
    config: WorldConfig,
    data: dict,
    *,
    seed_ticks: int = 60,
    seed_per_species_per_tick: int = 4,
    coverage_fraction: float = 1.0,
) -> tuple[PhasedPlan, object]:
    """Build a two-phase plan and return it with the probe simulation result.

    data: output of load_challenge_data().
    """
    plants: dict[str, PlantDefinition] = {p.plant: p for p in data["plants"]}
    idx = {p.plant: p.index for p in data["plants"]}
    unlocks = {u.plant: u.unlock for u in data["unlocks"]}
    classifications = data["classifications_mapping"]

    def new_sim() -> Simulator:
        return Simulator(
            config, data["plants"], animals=data["animals"],
            classifications=classifications, unlocks=unlocks,
            assumptions=EngineAssumptions(spread_enabled=True),
        )

    # ---- Phase 1: seed the initial species to drive unlocks ----
    n_init = len(INITIAL_SPECIES)
    band = config.height / n_init
    zones = {sp: range(int(round(i * band)), int(round((i + 1) * band))) for i, sp in enumerate(INITIAL_SPECIES)}
    gens = {sp: _seed_zone_cells(zones[sp], config.width) for sp in INITIAL_SPECIES}
    actions: dict[int, list[tuple[int, int, int]]] = {}
    for tk in range(0, min(seed_ticks, config.total_ticks)):
        row: list[tuple[int, int, int]] = []
        for sp in INITIAL_SPECIES:
            for _ in range(seed_per_species_per_tick):
                try:
                    r, c = next(gens[sp])
                except StopIteration:
                    continue
                row.append((idx[sp], r, c))
        if row:
            actions[tk] = row[: config.max_actions_per_tick]

    # Probe: run phase 1 only, discover which species get unlocked.
    probe = new_sim().run(dict(actions))
    unlocked = sorted(probe.unlocked_species, key=lambda s: idx.get(s, 999))

    # ---- Phase 2: balanced survival-window fill of all unlocked species ----
    start, end = survival_window(config.total_ticks)
    window_ticks = end - start + 1
    budget = window_ticks * config.max_actions_per_tick

    fill_species = [plants[s] for s in unlocked if s in plants]
    fill_species = order_species_for_shade(fill_species)
    n = len(fill_species)

    target = min(int(config.cmax * coverage_fraction), budget)
    target -= target % n
    per_species = max(1, target // n)

    band2 = config.height / n
    fill_actions: list[tuple[int, int, int]] = []
    pools: dict[str, list[tuple[int, int]]] = {}
    for i, sp in enumerate(fill_species):
        rs = int(round(i * band2))
        re = int(round((i + 1) * band2))
        cells: list[tuple[int, int]] = []
        for r in range(rs, re):
            for c in range(config.width):
                cells.append((r, c))
                if len(cells) >= per_species:
                    break
            if len(cells) >= per_species:
                break
        pools[sp.plant] = cells

    # Round-robin interleave for per-tick balance; casters naturally later.
    def is_caster(sp: PlantDefinition) -> bool:
        return any(r.get("type") == "shade_radius" for r in sp.rules.special)

    non_casters = [sp for sp in fill_species if not is_caster(sp)]
    casters = [sp for sp in fill_species if is_caster(sp)]

    def interleave(group: list[PlantDefinition]):
        cursors = {sp.plant: 0 for sp in group}
        remaining = True
        while remaining:
            remaining = False
            for sp in group:
                cells = pools[sp.plant]
                cur = cursors[sp.plant]
                if cur < len(cells):
                    r, c = cells[cur]
                    fill_actions.append((sp.index, r, c))
                    cursors[sp.plant] += 1
                    remaining = True

    interleave(non_casters)
    interleave(casters)

    per = config.max_actions_per_tick
    for i, action in enumerate(fill_actions):
        tick = min(end, start + i // per)
        actions.setdefault(tick, [])
        # window plantings replace any seed action on the same tick slot
        actions[tick].append(action)

    # Cap each tick at max_actions_per_tick (window ticks were sized to budget,
    # but seed ticks are separate and earlier so no overlap in practice).
    for tk in list(actions):
        actions[tk] = actions[tk][: config.max_actions_per_tick]

    plan = PhasedPlan(actions_by_tick=actions, unlocked_at_window=unlocked, survival_window=(start, end))
    return plan, probe
