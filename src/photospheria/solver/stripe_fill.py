"""Vertical-stripe balanced fill planner (spread-containment strategy).

Learned from the official Level 1-4 evaluation logs: uncontrolled spread turns
the garden into a Grass/Dwarf-Sunflower monoculture, crashing entropy (the 80%
score term) to ~0.29-0.32. Manual placement on an already-occupied cell is
DENIED, so late "rebalancing" plantings fail once a spreader has filled a cell.

This planner assigns each of the five guaranteed starter species its own
full-height vertical column stripe. Because a species only borders two others
(and only along a thin vertical seam), spread mostly stays *inside* a species'
own stripe, which is diversity-neutral (same species). This keeps entropy far
higher than the interleaved band layout that was previously submitted, while
still filling most of the grid.

All placements are scheduled inside the survival window (last ~99 ticks) so the
manually placed cells are alive at the final tick. Placements are round-robin
across species so each tick's 20-action batch is balanced.

Deterministic for fixed inputs.
"""

from __future__ import annotations

from dataclasses import dataclass

from photospheria.data.models import PlantDefinition
from photospheria.simulation.full_engine import WorldConfig
from photospheria.solver.balanced_fill import survival_window


@dataclass(frozen=True)
class StripePlan:
    actions_by_tick: dict[int, list[tuple[int, int, int]]]
    species_order: list[str]
    survival_window: tuple[int, int]
    stripes: dict[str, tuple[int, int]]  # species -> (col_start, col_end_exclusive)

    def total_actions(self) -> int:
        return sum(len(v) for v in self.actions_by_tick.values())


def plan_stripe_fill(
    config: WorldConfig,
    species: list[PlantDefinition],
    *,
    nutrient_capacity: int = 100,
) -> StripePlan:
    """Assign each species a vertical column stripe and fill it in the window.

    species: ordered starter species; order maps left-to-right to stripes.
    """
    n = len(species)
    W, H, T = config.width, config.height, config.total_ticks
    start, end = survival_window(T, nutrient_capacity)
    window_ticks = end - start + 1
    budget = window_ticks * config.max_actions_per_tick

    stripe_w = W // n
    stripes: dict[str, tuple[int, int]] = {}
    pools: dict[str, list[tuple[int, int]]] = {}
    for i, sp in enumerate(species):
        c0 = i * stripe_w
        c1 = (i + 1) * stripe_w if i < n - 1 else W
        stripes[sp.plant] = (c0, c1)
        # Column-major within the stripe: fill column by column, top to bottom.
        pools[sp.plant] = [(r, c) for c in range(c0, c1) for r in range(H)]

    # Balanced: each species gets the same count, capped by the smallest stripe
    # and by the survival-window action budget.
    per = min(min(len(p) for p in pools.values()), budget // n)

    # Round-robin interleave so every 20-action tick batch is balanced.
    seq: list[tuple[int, int, int]] = []
    idx_of = {sp.plant: sp.index for sp in species}
    for i in range(per):
        for sp in species:
            r, c = pools[sp.plant][i]
            seq.append((idx_of[sp.plant], r, c))

    actions_by_tick: dict[int, list[tuple[int, int, int]]] = {}
    per_tick = config.max_actions_per_tick
    for i, action in enumerate(seq):
        tick = min(end, start + i // per_tick)
        actions_by_tick.setdefault(tick, []).append(action)

    return StripePlan(
        actions_by_tick=actions_by_tick,
        species_order=[sp.plant for sp in species],
        survival_window=(start, end),
        stripes=stripes,
    )
