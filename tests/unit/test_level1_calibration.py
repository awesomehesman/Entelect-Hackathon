from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_level1_calibration import INITIAL_SPECIES, build_candidate, generate


def test_calibration_candidate_uses_only_initial_species_and_tick_499(tmp_path: Path) -> None:
    resource = Path(__file__).parents[2] / "Artifacts" / "additional-resources" / "plant_dataset.json"
    candidate = build_candidate(resource)
    plants = candidate["actions"][0]["plants"]

    assert candidate["actions"][0]["tick"] == 499
    assert len(plants) == 5
    assert len({(item["row"], item["col"]) for item in plants}) == 5
    assert all(0 <= item["row"] < 50 and 0 <= item["col"] < 50 for item in plants)
    assert all("plant_index" in item and "index" not in item for item in plants)
    assert len({name for name, _, _ in INITIAL_SPECIES}) == 5


def test_calibration_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = generate(tmp_path / "first.json")
    second = generate(tmp_path / "second.json")
    assert first.read_bytes() == second.read_bytes()
    assert json.loads(first.read_text(encoding="utf-8")) == json.loads(second.read_text(encoding="utf-8"))