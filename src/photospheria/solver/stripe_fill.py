"""Spread-aware isolated planting strategy with spread avoidance.

CRITICAL INSIGHT from evaluator logs:
- Planting on cells already occupied by spread = DENIED
- Grass(1) and DwarfSunflower(5) spread FAST - within ~20 ticks they can
  spread 3-4 cells away from seed position
- Many denials happen in rows 2-5 from spread of row 0-1 plants

Strategy: 
1. Plant species in VERTICAL STRIPES (each species owns columns, not rows)
2. Each stripe is separated by empty columns to slow cross-stripe spread
3. Plant from BOTTOM-UP within each stripe (furthest from row 0)
4. This isolates each species' spread territory

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
    """Vertical stripe planting with spread barriers.
    
    Each species gets a vertical stripe (column range).
    Stripes separated by 1 empty column as spread buffer.
    Plants within stripe are filled bottom-to-top to maximize distance.
    """
    n = len(species)
    W, H, T = config.width, config.height, config.total_ticks
    start, end = survival_window(T, nutrient_capacity)
    window_ticks = end - start + 1
    budget = window_ticks * config.max_actions_per_tick
    
    # Vertical stripes with 1-column gaps
    gap = 1
    stripe_w = (W - gap * (n - 1)) // n
    
    idx_of = {sp.plant: sp.index for sp in species}
    pools: dict[str, list[tuple[int, int]]] = {}
    stripes: dict[str, tuple[int, int]] = {}
    
    for i, sp in enumerate(species):
        c_start = i * (stripe_w + gap)
        c_end = c_start + stripe_w
        if i == n - 1:
            c_end = W  # Last stripe takes remaining columns
        
        stripes[sp.plant] = (c_start, c_end)
        
        # Build cells BOTTOM-UP (highest row first) for maximum spread distance
        cells = []
        for r in range(H - 1, -1, -1):  # Bottom to top
            for c in range(c_start, c_end):
                cells.append((r, c))
        pools[sp.plant] = cells
    
    # Equal distribution
    per_species = budget // n
    counts = {sp.plant: min(per_species, len(pools[sp.plant])) for sp in species}
    
    # Distribute remainder
    remaining = budget - sum(counts.values())
    for sp in species:
        if remaining <= 0:
            break
        if counts[sp.plant] < len(pools[sp.plant]):
            counts[sp.plant] += 1
            remaining -= 1
    
    # Build interleaved sequence (round-robin)
    seq: list[tuple[int, int, int]] = []
    pointers = {sp.plant: 0 for sp in species}
    
    max_count = max(counts.values())
    for i in range(max_count):
        for sp in species:
            if i < counts[sp.plant]:
                r, c = pools[sp.plant][pointers[sp.plant]]
                seq.append((idx_of[sp.plant], r, c))
                pointers[sp.plant] += 1
    
    # Distribute to ticks
    actions_by_tick: dict[int, list[tuple[int, int, int]]] = {}
    per_tick = config.max_actions_per_tick
    
    for i, action in enumerate(seq):
        tick = start + i // per_tick
        if tick > end:
            tick = end
        actions_by_tick.setdefault(tick, []).append(action)

    return StripePlan(
        actions_by_tick=actions_by_tick,
        species_order=[sp.plant for sp in species],
        survival_window=(start, end),
        stripes=stripes,
        weights=counts,
    )
