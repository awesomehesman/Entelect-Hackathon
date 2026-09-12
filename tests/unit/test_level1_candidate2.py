from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_level1_candidate2 import build_candidate


def test_candidate2_has_balanced_valid_action_batches() -> None:
    resource = Path(__file__).parents[2] / "Artifacts" / "additional-resources" / "plant_dataset.json"
    candidate, diagnostics = build_candidate(resource)
    all_actions = [plant for group in candidate["actions"] for plant in group["plants"]]
    assert len(all_actions) == 1980
    assert len(candidate["actions"]) == 99
    assert all(len(group["plants"]) == 20 for group in candidate["actions"])
    assert len({(plant["row"], plant["col"]) for plant in all_actions}) == 1980
    assert candidate["actions"][0]["tick"] == 401
    assert candidate["actions"][-1]["tick"] == 499
    assert all(401 <= group["tick"] <= 499 for group in candidate["actions"])
    assert diagnostics["exposure_ticks"]["maximum"] < 100
    assert diagnostics["exposure_ticks"]["minimum"] == 1
    assert all("plant_index" in plant and "index" not in plant for plant in all_actions)
    counts = {1: 0, 2: 0, 5: 0, 6: 0, 12: 0}
    for plant in all_actions:
        counts[plant["plant_index"]] += 1
    assert counts == {1: 396, 2: 396, 5: 396, 6: 396, 12: 396}
    assert diagnostics["expected_final_counts_no_spread"] == {"Grass": 396, "Rose Bush": 396, "Lavender": 396, "Dwarf Sunflower": 396, "Oak Tree": 396}
    assert diagnostics["predicted_leaderboard_score_1e9_scale"] == 312795056
    assert diagnostics["expected_average_lifespan_k_1_by_species"]["Grass"] == 89.5959595959596
    assert diagnostics["expected_average_lifespan_k_1_by_species"]["Oak Tree"] == 10.404040404040405
    assert diagnostics["shade_risk"]["grass_target_cells_in_possible_oak_shade"] == 0
    assert diagnostics["shade_risk"]["dwarf_sunflower_target_cells_in_possible_oak_shade"] == 0


def test_candidate2_generation_is_deterministic(tmp_path: Path) -> None:
    resource = Path(__file__).parents[2] / "Artifacts" / "additional-resources" / "plant_dataset.json"
    first, _ = build_candidate(resource)
    second, _ = build_candidate(resource)
    assert json.dumps(first, indent=2) == json.dumps(second, indent=2)