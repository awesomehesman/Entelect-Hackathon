from __future__ import annotations

from photospheria.core.models import PlantInstance, World
from photospheria.data.models import PlantDefinition
from photospheria.exceptions import AmbiguousMechanicError, ValidationError
from photospheria.levels.base import LevelConfig
from photospheria.mechanics.spread import spread_targets
from photospheria.simulation.nutrients import drain_occupied_cell, regenerate_dead_matter
from photospheria.simulation.seasons import season_at
from photospheria.simulation.shade import refresh_shade


def advance_to(world: World, config: LevelConfig, tick: int) -> None:
    if tick < world.current_tick or tick >= config.total_ticks:
        raise ValidationError("World ticks must advance monotonically within the level.")
    for next_tick in range(world.current_tick + 1, tick + 1):
        process_environment_tick(world, config, next_tick)


def process_environment_tick(world: World, config: LevelConfig, tick: int) -> None:
    world.current_tick = tick
    if config.seasons_enabled:
        world.season = season_at(config.season_schedule, tick, config.total_ticks)
    for row in world.cells:
        for cell in row:
            if cell.plant is not None and cell.plant.alive:
                if drain_occupied_cell(cell):
                    cell.plant.alive = False
                    cell.plant.death_tick = tick
                    cell.dead_matter = True
                    cell.plant = None
            else:
                regenerate_dead_matter(cell)


def plant_explicitly(world: World, config: LevelConfig, species: PlantDefinition, row: int, col: int, tick: int) -> None:
    advance_to(world, config, tick)
    World.plant_explicitly(world, species, row, col, tick)


def run_tick(world: World, config: LevelConfig, actions: list[tuple[PlantDefinition, int, int]], definitions: dict[str, PlantDefinition]) -> None:
    config.validate_tick_action_count(len(actions)) if hasattr(config, "validate_tick_action_count") else _validate_action_count(config, len(actions))
    refresh_shade(world, definitions)
    for species, row, col in actions:
        plant_explicitly(world, config, species, row, col, world.current_tick)
    refresh_shade(world, definitions)
    for row in world.cells:
        for cell in row:
            plant = cell.plant
            if plant is None or not plant.alive:
                continue
            definition = definitions[plant.species]
            if any(rule.get("type") == "adjacent_shade_penalty" for rule in definition.rules.special) and cell.shade:
                raise AmbiguousMechanicError("AMB-011", "adjacent_shade_penalty magnitude and ordering are unresolved.")
            if any(rule.get("type") == "no_shade_survival" for rule in definition.rules.weaknesses) and cell.shade:
                plant.alive = False
                plant.death_tick = world.current_tick
                cell.dead_matter = True
                cell.plant = None
    if world.current_tick + 1 < config.total_ticks:
        process_environment_tick(world, config, world.current_tick + 1)


def _validate_action_count(config: LevelConfig, count: int) -> None:
    if not 0 <= count <= config.max_actions_per_tick:
        raise ValidationError(f"A tick may contain at most {config.max_actions_per_tick} actions.")


def spread_once(world: World, config: LevelConfig, species: PlantDefinition, source_row: int, source_col: int, tick: int) -> tuple[tuple[int, int], ...]:
    source = world.cell(source_row, source_col)
    if source.plant is None or not source.plant.is_mature(tick):
        return ()
    if any(rule.get("type") == "no_winter_spread" for rule in species.rules.weaknesses) and world.season == "Winter":
        return ()
    if species.growth.spread_rate <= 0 or (tick - source.plant.birth_tick) % species.growth.spread_rate != 0:
        return ()
    if any(rule.get("type") == "no_shade_spread" for rule in species.rules.weaknesses) and source.shade:
        return ()
    return tuple(spread_targets(source_col, source_row, world.width, world.height, species.growth.spread_type, species.growth.spread_range))