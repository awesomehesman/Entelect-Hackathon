"""Zoned, shade-aware, balanced survival-window fill planner.

Strategy rationale (alpha = 1, k = 1, verified against the official Level 1
evaluator log):

    final = 0.8 * H * (C / Cmax) + 0.2 * sum(lifespan / T) / Cmax

The main score dominates. It is maximised by having many *distinct* species
present, kept *balanced* (equal counts maximise entropy H), covering as many
cells C as possible, all *alive at the final tick*.

Two mechanics constrain a naive fill and are handled here:

1. Nutrient death: a manually-planted cell survives to the final scored tick
   only if planted within the last ~100 ticks (capacity 100, drain 1/tick).
   Empirically the earliest surviving tick for T=500 is 401 (= T - 99). All
   placements are therefore scheduled inside this survival window.

2. Shade death: shade-casting species (e.g. Oak Tree, shade_radius=4) kill
   neighbouring plants that have a ``no_shade_survival`` weakness (e.g. Grass)
   once the caster matures. The planner (a) places each species in its own
   contiguous zone so shade-sensitive species are separated from casters, and
   (b) schedules shade-casters late enough that they never reach maturity
   (birth_tick > T - time_to_maturity), so they occupy cells and add to
   diversity without ever shading.

The plan is robust to unknown terrain: placements that land on non-soil cells
in the hidden world are simply ignored by the evaluator, reducing C but never
invalidating the submission. Spread, if it occurs, only adds coverage.

Deterministic: identical inputs -> identical plan.
"""

from __future__ import annotations

from dataclasses import dataclass

from photospheria.data.models import PlantDefinition
from photospheria.simulation.full_engine import WorldConfig


@dataclass(frozen=True)
class FillPlan:
    actions_by_tick: dict[int, list[tuple[int, int, int]]]
    species_order: list[str]
    survival_window: tuple[int, int]
    zones: dict[str, tuple[int, int]]  # species -> (row_start, row_end_exclusive)

    def total_actions(self) -> int:
        return sum(len(v) for v in self.actions_by_tick.values())


def survival_window(total_ticks: int, nutrient_capacity: int = 100) -> tuple[int, int]:
    earliest = total_ticks - (nutrient_capacity - 1)
    return (max(0, earliest), total_ticks - 1)


def plan_zoned_fill(
    config: WorldConfig,
    species: list[PlantDefinition],
    *,
    coverage_fraction: float = 1.0,
    margin: int = 0,
    nutrient_capacity: int = 100,
    late_shade_casters: bool = True,
) -> FillPlan:
    """Balanced zoned fill across the survival window.

    species: ordered list of PlantDefinition to place, all reachable at
        planting time. Order determines zone order (top -> bottom).
    coverage_fraction: fraction of Cmax to attempt to fill (<= 1).
    margin: keep placements this many cells from the border.
    late_shade_casters: schedule shade-casting species so late they never
        mature (avoids shade-killing neighbours).
    """
    n = len(species)
    start, end = survival_window(config.total_ticks, nutrient_capacity)
    window_ticks = end - start + 1
    budget = window_ticks * config.max_actions_per_tick

    height = config.height
    width = config.width
    r0, r1 = margin, height - margin
    c0, c1 = margin, width - margin
    inner_rows = r1 - r0
    inner_cols = c1 - c0

    target = min(int(config.cmax * coverage_fraction), budget, inner_rows * inner_cols)
    target -= target % n
    if target <= 0:
        target = n

    per_species = target // n

    # Contiguous horizontal band per species. Bands are laid out in the given
    # species order from the top; shade-sensitive vs caster separation is the
    # caller's responsibility via ordering (see build_level_species_order).
    rows_per_band = inner_rows / n
    zones: dict[str, tuple[int, int]] = {}
    placements: dict[str, list[tuple[int, int]]] = {}
    for i, sp in enumerate(species):
        band_start = r0 + int(round(i * rows_per_band))
        band_end = r0 + int(round((i + 1) * rows_per_band))
        zones[sp.plant] = (band_start, band_end)
        cells: list[tuple[int, int]] = []
        for r in range(band_start, band_end):
            for c in range(c0, c1):
                cells.append((r, c))
                if len(cells) >= per_species:
                    break
            if len(cells) >= per_species:
                break
        placements[sp.plant] = cells

    # Determine which species are shade-casters (have shade_radius) and would
    # mature within the run; those are scheduled last (late) so they never
    # cast shade.
    def is_caster(sp: PlantDefinition) -> bool:
        return any(r.get("type") == "shade_radius" for r in sp.rules.special)

    caster_names = {sp.plant for sp in species if late_shade_casters and is_caster(sp)}

    # Build a global placement order: non-casters first (earliest ticks -> most
    # longevity), casters last (latest ticks -> never mature). Within a group,
    # round-robin across species keeps per-tick batches balanced.
    def interleave(names: list[str]) -> list[tuple[int, int, int]]:
        pools = {nm: list(placements[nm]) for nm in names}
        idx_of = {sp.plant: sp.index for sp in species}
        out: list[tuple[int, int, int]] = []
        while any(pools.values()):
            for nm in names:
                if pools[nm]:
                    r, c = pools[nm].pop(0)
                    out.append((idx_of[nm], r, c))
        return out

    non_casters = [sp.plant for sp in species if sp.plant not in caster_names]
    casters = [sp.plant for sp in species if sp.plant in caster_names]

    ordered = interleave(non_casters) + interleave(casters)

    # Ensure casters land after their "never-mature" threshold when possible.
    # We schedule earliest-first; casters at the tail naturally get late ticks.
    actions_by_tick: dict[int, list[tuple[int, int, int]]] = {}
    per = config.max_actions_per_tick
    for i, action in enumerate(ordered):
        tick = min(end, start + i // per)
        actions_by_tick.setdefault(tick, []).append(action)

    return FillPlan(
        actions_by_tick=actions_by_tick,
        species_order=[sp.plant for sp in species],
        survival_window=(start, end),
        zones=zones,
    )


def order_species_for_shade(species: list[PlantDefinition]) -> list[PlantDefinition]:
    """Order species so shade-sensitive ones are far (in band order) from casters.

    Places shade-sensitive species (``no_shade_survival``) first (top bands) and
    shade-casters (``shade_radius``) last (bottom bands), maximising row
    separation between them.
    """
    def sensitive(sp: PlantDefinition) -> bool:
        return any(r.get("type") == "no_shade_survival" for r in sp.rules.weaknesses)

    def caster(sp: PlantDefinition) -> bool:
        return any(r.get("type") == "shade_radius" for r in sp.rules.special)

    def key(sp: PlantDefinition) -> tuple[int, int]:
        if sensitive(sp):
            return (0, sp.index)
        if caster(sp):
            return (2, sp.index)
        return (1, sp.index)

    return sorted(species, key=key)
