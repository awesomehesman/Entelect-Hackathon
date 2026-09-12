from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from photospheria.core.models import Cell, PlantInstance, World as CoreWorld
from photospheria.data.models import PlantDefinition
from photospheria.exceptions import AmbiguousMechanicError, ValidationError
from photospheria.levels.level1 import LEVEL1_SEASON_SCHEDULE, Level1Constraints
from photospheria.scoring.engine import diversity_entropy
from photospheria.simulation.engine import advance_to, plant_explicitly, run_tick as shared_run_tick, spread_once as shared_spread_once
from photospheria.simulation.shade import refresh_shade


class World(CoreWorld):
    @classmethod
    def create_level1(cls, soil_grid: list[list[int]], terrain: dict[tuple[int, int], Iterable[str]] | None = None) -> "World":
        base = CoreWorld.from_config(Level1Constraints(), soil_grid, terrain)
        return cls(base.width, base.height, base.total_ticks, base.cells, unlocked_species=set())

    def advance_to(self, tick: int) -> None:
        advance_to(self, Level1Constraints(), tick)

    def _process_environment_tick(self, tick: int) -> None:
        advance_to(self, Level1Constraints(), tick)

    def refresh_shade(self, definitions: dict[str, PlantDefinition]) -> None:
        refresh_shade(self, definitions)

    def plant_explicitly(self, species: PlantDefinition, row: int, col: int, tick: int) -> None:
        plant_explicitly(self, Level1Constraints(), species, row, col, tick)

    def run_tick(self, actions: list[tuple[PlantDefinition, int, int]], definitions: dict[str, PlantDefinition]) -> None:
        shared_run_tick(self, Level1Constraints(), actions, definitions)


@dataclass(frozen=True)
class Level1ScoreDiagnostics:
    occupied_cells: int
    species_counts: dict[str, int]
    entropy: float
    occupancy_ratio: float
    lifespans: tuple[int, ...]

    def main_score(self, alpha: float) -> float:
        return self.entropy * self.occupancy_ratio**alpha

    def longevity_score(self, k: float, total_ticks: int = 500, maximum_cells: int = 2500) -> float:
        return sum((lifespan / total_ticks) ** k for lifespan in self.lifespans) / maximum_cells


def score_diagnostics(world: World) -> Level1ScoreDiagnostics:
    plants = [cell.plant for row in world.cells for cell in row if cell.plant and cell.plant.alive]
    counts: dict[str, int] = {}
    for plant in plants:
        counts[plant.species] = counts.get(plant.species, 0) + 1
    return Level1ScoreDiagnostics(len(plants), counts, diversity_entropy(counts, 31), len(plants) / (world.width * world.height), tuple(plant.lifespan_at(world.current_tick) for plant in plants))


def spread_once(world: World, species: PlantDefinition, source_row: int, source_col: int, tick: int) -> tuple[tuple[int, int], ...]:
    return shared_spread_once(world, Level1Constraints(), species, source_row, source_col, tick)
