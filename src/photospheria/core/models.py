from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from photospheria.data.models import PlantDefinition
from photospheria.exceptions import ValidationError


@dataclass
class PlantInstance:
    species: str
    index: int
    birth_tick: int
    time_to_maturity: int
    alive: bool = True
    death_tick: int | None = None

    def age_at(self, tick: int) -> int:
        return max(0, tick - self.birth_tick)

    def is_mature(self, tick: int) -> bool:
        return self.age_at(tick) >= self.time_to_maturity

    def lifespan_at(self, tick: int) -> int:
        end = self.death_tick if self.death_tick is not None else tick + 1
        return max(0, end - self.birth_tick)


@dataclass
class Cell:
    row: int
    col: int
    soil_type: int
    terrain: frozenset[str] = frozenset()
    nutrients: float = 100.0
    dead_matter: bool = False
    shade: bool = False
    plant: PlantInstance | None = None

    @property
    def usable(self) -> bool:
        return not (self.terrain & {"stone", "path", "water"})


@dataclass
class World:
    width: int
    height: int
    total_ticks: int
    cells: list[list[Cell]]
    current_tick: int = 0
    season: str = "Spring"
    unlocked_species: set[str] = field(default_factory=set)

    @classmethod
    def from_config(cls, config: object, soil_grid: list[list[int]], terrain: dict[tuple[int, int], Iterable[str]] | None = None) -> "World":
        width = int(getattr(config, "width"))
        height = int(getattr(config, "height"))
        if len(soil_grid) != height or any(len(row) != width for row in soil_grid):
            raise ValidationError("soil_grid dimensions do not match LevelConfig.")
        terrain = terrain or {}
        cells = [[Cell(row, col, int(soil_grid[row][col]), frozenset(terrain.get((row, col), ()))) for col in range(width)] for row in range(height)]
        return cls(width, height, int(getattr(config, "total_ticks")), cells)

    def cell(self, row: int, col: int) -> Cell:
        if not 0 <= row < self.height or not 0 <= col < self.width:
            raise ValidationError("Cell coordinate is outside the world.")
        return self.cells[row][col]

    def plant_explicitly(self, species: PlantDefinition, row: int, col: int, tick: int) -> None:
        if not 0 <= tick < self.total_ticks:
            raise ValidationError(f"Tick must be in 0..{self.total_ticks - 1}: {tick}")
        cell = self.cell(row, col)
        if not cell.usable:
            raise ValidationError("Cannot plant on blocked terrain.")
        if cell.soil_type not in species.preferred_soil:
            raise ValidationError("Plant soil preference does not match the cell.")
        if species.plant not in self.unlocked_species:
            raise ValidationError(f"Species is not unlocked: {species.plant}")
        if cell.plant is not None:
            cell.plant.alive = False
            cell.plant.death_tick = tick
            cell.dead_matter = True
        cell.plant = PlantInstance(species.plant, species.index, tick, species.growth.time_to_maturity)
        cell.dead_matter = False