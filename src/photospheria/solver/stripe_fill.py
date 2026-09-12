"""Dense balanced fill planner optimized for animal spawning.

Strategy: Maximize coverage of all 5 starters to trigger animal appearance
conditions on Levels 2-4 (where animals are enabled). Animals gate many
plant unlocks, so more animals → more species → higher entropy → higher scores.

Animal triggers from animals.json:
- Loamcrawlers: Grass >= 5% coverage
- Nectaris: Lavender >= 2% OR flowering group >= 2%
- Solwings: Dwarf Sunflower >= 3% AND Rose >= 2%
- Grazeleths: Grass >= 5% AND Rose >= 10 count
- Canorals: Lavender >= 10 count AND Grass >= 10 count
- Pollinex: Grass >= 4% AND flowering plants >= 10 count

All placements in survival window so they're alive at scoring.
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
    stripes: dict[str, tuple[int, int]]
    weights: dict[str, int]

    def total_actions(self) -> int:
        return sum(len(v) for v in self.actions_by_tick.values())


def plan_stripe_fill(
    config: WorldConfig,
    species: list[PlantDefinition],
    *,
    nutrient_capacity: int = 100,
    use_weights: bool = True,
) -> StripePlan:
    """Plant maximum density of all species to trigger animal spawns.
    
    Uses entire survival window budget, interleaved across the grid.
    """
    n = len(species)
    W, H, T = config.width, config.height, config.total_ticks
    start, end = survival_window(T, nutrient_capacity)
    window_ticks = end - start + 1
    budget = window_ticks * config.max_actions_per_tick
    
    # All cells in row-major order
    all_cells = [(r, c) for r in range(H) for c in range(W)]
    
    # Equal distribution to maintain diversity
    per_species = budget // n
    counts = {sp.plant: per_species for sp in species}
    
    # Use any remaining budget
    remaining = budget - (per_species * n)
    for sp in species:
        if remaining <= 0:
            break
        counts[sp.plant] += 1
        remaining -= 1
    
    # Build interleaved sequence (round-robin across the full grid)
    idx_of = {sp.plant: sp.index for sp in species}
    seq: list[tuple[int, int, int]] = []
    
    cell_idx = 0
    for i in range(per_species + 1):  # +1 for remainder
        for sp in species:
            if i < counts[sp.plant] and cell_idx < len(all_cells):
                r, c = all_cells[cell_idx]
                seq.append((idx_of[sp.plant], r, c))
                cell_idx += 1
    
    # Distribute to ticks (maximize actions per tick)
    actions_by_tick: dict[int, list[tuple[int, int, int]]] = {}
    per_tick = config.max_actions_per_tick
    for i, action in enumerate(seq):
        tick = min(end, start + i // per_tick)
        actions_by_tick.setdefault(tick, []).append(action)

    return StripePlan(
        actions_by_tick=actions_by_tick,
        species_order=[sp.plant for sp in species],
        survival_window=(start, end),
        stripes={},
        weights=counts,
    )
