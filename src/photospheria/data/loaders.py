from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from photospheria.data.models import (
    AnimalDefinition,
    ClassificationGroup,
    LevelDefinition,
    PlantDefinition,
    UnlockDefinition,
)
from photospheria.data.validators import validate_authoritative_dataset
from photospheria.exceptions import ValidationError, WorldLoadError


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_challenge_data(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    resources_dir = base / "Artifacts" / "additional-resources"

    plants_raw = load_json(resources_dir / "plant_dataset.json")
    unlocks_raw = load_json(resources_dir / "plant_unlock_conditions.json")
    animals_raw = load_json(resources_dir / "animals.json")
    classifications_raw = load_json(resources_dir / "classifications.json")

    plants = [PlantDefinition.from_raw(item) for item in plants_raw]
    unlocks = [UnlockDefinition.from_raw(item) for item in unlocks_raw]
    animals = [AnimalDefinition.from_raw(item) for item in animals_raw]
    classifications = [
        ClassificationGroup.from_mapping(name, members)
        for name, members in classifications_raw.items()
    ]

    validate_authoritative_dataset(plants, unlocks, animals, classifications)

    return {
        "plants": plants,
        "unlocks": unlocks,
        "animals": animals,
        "classifications": classifications,
        "classifications_mapping": classifications_raw,
    }


def load_level_definition(path: str | Path) -> LevelDefinition:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise WorldLoadError("Level definition must be a JSON object.")

    required_fields = {"width", "height", "total_ticks", "soil_grid"}
    missing = sorted(required_fields - set(payload))
    if missing:
        raise WorldLoadError(f"Missing required level fields: {missing}")

    width = int(payload["width"])
    height = int(payload["height"])
    total_ticks = int(payload["total_ticks"])
    soil_grid = payload["soil_grid"]

    if width <= 0 or height <= 0:
        raise WorldLoadError("Level width and height must be positive integers.")

    if len(soil_grid) != height:
        raise WorldLoadError("soil_grid height does not match level height.")
    if any(len(row) != width for row in soil_grid):
        raise WorldLoadError("soil_grid width does not match level width.")

    for row_index, row in enumerate(soil_grid):
        for col_index, cell in enumerate(row):
            if not isinstance(cell, int):
                raise WorldLoadError(
                    f"soil_grid[{row_index}][{col_index}] must be an int; got {type(cell).__name__}."
                )

    return LevelDefinition(
        width=width,
        height=height,
        total_ticks=total_ticks,
        soil_grid=[[int(v) for v in row] for row in soil_grid],
        terrain_features=payload.get("terrain_features"),
        season_schedule=payload.get("season_schedule", []),
        event_schedule=payload.get("event_schedule", []),
    )
