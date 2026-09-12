from __future__ import annotations

import json
from pathlib import Path

import pytest

from photospheria.data.models import PlantDefinition
from photospheria.exceptions import ValidationError
from photospheria.simulation.level1 import World, score_diagnostics


def _definitions() -> dict[str, PlantDefinition]:
    path = Path(__file__).parents[2] / "Artifacts" / "additional-resources" / "plant_dataset.json"
    return {item["plant"]: PlantDefinition.from_raw(item) for item in json.loads(path.read_text())}


def test_level1_world_planting_maturity_nutrients_and_replacement() -> None:
    definitions = _definitions()
    world = World.create_level1([[0] * 50 for _ in range(50)])
    world.unlocked_species = {"Grass", "Oak Tree"}
    world.plant_explicitly(definitions["Grass"], 25, 25, 0)
    assert world.cell(25, 25).plant is not None
    assert not world.cell(25, 25).plant.is_mature(0)
    world.advance_to(1)
    assert world.cell(25, 25).plant is not None
    assert world.cell(25, 25).nutrients == 99
    world.plant_explicitly(definitions["Oak Tree"], 25, 25, 1)
    assert world.cell(25, 25).plant.species == "Oak Tree"


def test_level1_world_rejects_wrong_soil_and_blocked_terrain() -> None:
    definitions = _definitions()
    world = World.create_level1([[2] * 50 for _ in range(50)], {(1, 1): {"path"}})
    world.unlocked_species = {"Grass"}
    with pytest.raises(ValidationError):
        world.plant_explicitly(definitions["Grass"], 0, 0, 0)
    with pytest.raises(ValidationError):
        world.plant_explicitly(definitions["Grass"], 1, 1, 0)


def test_oak_shade_and_score_diagnostics_are_exposed() -> None:
    definitions = _definitions()
    world = World.create_level1([[0] * 50 for _ in range(50)])
    world.unlocked_species = {"Oak Tree", "Grass"}
    world.plant_explicitly(definitions["Oak Tree"], 25, 25, 0)
    world.advance_to(20)
    world.refresh_shade(definitions)
    assert world.cell(25, 29).shade
    diagnostics = score_diagnostics(world)
    assert diagnostics.species_counts == {"Oak Tree": 1}
    assert diagnostics.occupancy_ratio == pytest.approx(1 / 2500)