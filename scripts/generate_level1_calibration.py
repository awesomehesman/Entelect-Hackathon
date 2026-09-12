#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TICK = 499
WIDTH = 50
HEIGHT = 50
INITIAL_SPECIES = (
    ("Grass", 25, 25),
    ("Rose Bush", 25, 26),
    ("Lavender", 26, 25),
    ("Dwarf Sunflower", 26, 26),
    ("Oak Tree", 24, 25),
)


def build_candidate(resource_path: Path) -> dict[str, Any]:
    plants = json.loads(resource_path.read_text(encoding="utf-8"))
    indices = {str(item["plant"]): int(item["index"]) for item in plants}
    missing = [name for name, _, _ in INITIAL_SPECIES if name not in indices]
    if missing:
        raise ValueError(f"Initial species missing from plant dataset: {missing}")

    coordinates = [(row, col) for _, row, col in INITIAL_SPECIES]
    if TICK < 0 or TICK >= 500:
        raise ValueError(f"Invalid calibration tick: {TICK}")
    if any(not 0 <= row < HEIGHT or not 0 <= col < WIDTH for row, col in coordinates):
        raise ValueError("Calibration coordinate is outside the Level 1 bounds.")
    if len(coordinates) != len(set(coordinates)):
        raise ValueError("Calibration coordinates must be distinct.")
    if len(INITIAL_SPECIES) > 20:
        raise ValueError("Calibration candidate exceeds the per-tick action limit.")

    return {
        "actions": [
            {
                "tick": TICK,
                "plants": [
                    {"plant_index": indices[name], "row": row, "col": col}
                    for name, row, col in INITIAL_SPECIES
                ],
            }
        ]
    }


def generate(output_path: Path | None = None, resource_path: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[1]
    resource = resource_path or root / "Artifacts" / "additional-resources" / "plant_dataset.json"
    output = output_path or root / "output" / "level1" / "calibration-01" / "solution.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = build_candidate(resource)
    output.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    print(generate())