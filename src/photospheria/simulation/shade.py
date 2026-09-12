from __future__ import annotations

from photospheria.core.models import World
from photospheria.data.models import PlantDefinition


def refresh_shade(world: World, definitions: dict[str, PlantDefinition]) -> None:
    for row in world.cells:
        for cell in row:
            cell.shade = False
    for row in world.cells:
        for cell in row:
            plant = cell.plant
            if plant is None or not plant.alive or not plant.is_mature(world.current_tick):
                continue
            definition = definitions.get(plant.species)
            if definition is None:
                continue
            for rule in definition.rules.special:
                if rule.get("type") != "shade_radius":
                    continue
                radius = int(rule["value"])
                for target_row in range(max(0, cell.row - radius), min(world.height, cell.row + radius + 1)):
                    for target_col in range(max(0, cell.col - radius), min(world.width, cell.col + radius + 1)):
                        world.cells[target_row][target_col].shade = True