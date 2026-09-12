from __future__ import annotations

import json
from pathlib import Path

import pytest

from photospheria.exceptions import ValidationError
from photospheria.levels.level1 import (
    INITIAL_LEVEL1_SPECIES,
    Level1Constraints,
    Reachability,
    analyze_level1_reachability,
    build_level1_calibration_actions,
)


def _datasets() -> tuple[set[str], list[dict], set[str]]:
    root = Path(__file__).parents[2] / "Artifacts" / "additional-resources"
    plants = json.loads((root / "plant_dataset.json").read_text())
    unlocks = json.loads((root / "plant_unlock_conditions.json").read_text())
    animals = json.loads((root / "animals.json").read_text())
    return {item["plant"] for item in plants}, unlocks, {item["name"] for item in animals}


def test_level1_constraints_are_explicit() -> None:
    constraints = Level1Constraints()
    assert (constraints.width, constraints.height, constraints.total_ticks) == (50, 50, 500)
    assert constraints.seasons_enabled
    assert not constraints.animals_enabled
    assert not constraints.weather_enabled
    constraints.validate_action(0, 49, 49, "Grass", set(INITIAL_LEVEL1_SPECIES))
    with pytest.raises(ValidationError):
        constraints.validate_action(500, 0, 0, "Grass", set(INITIAL_LEVEL1_SPECIES))


def test_level1_reachability_is_five_initial_and_twenty_six_blocked() -> None:
    plants, unlocks, animals = _datasets()
    result = analyze_level1_reachability(plants, unlocks, animals)
    assert {item.species for item in result.values() if item.status == Reachability.DEFINITELY_REACHABLE} == INITIAL_LEVEL1_SPECIES
    assert sum(item.status == Reachability.DEFINITELY_UNREACHABLE for item in result.values()) == 26


def test_calibration_actions_are_deterministic_and_coordinate_valid() -> None:
    first = build_level1_calibration_actions()
    second = build_level1_calibration_actions()
    assert first == second
    assert len(first) == 5
    assert all(0 <= tick < 500 and 0 <= row < 50 and 0 <= col < 50 for tick, _, row, col in first)