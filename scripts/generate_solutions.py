#!/usr/bin/env python3
"""Generate best-known valid solutions for all levels.

For each level this:
  1. Builds the promoted robust plan (zoned, balanced, survival-window fill of
     the guaranteed-reachable starter species). This plan is terrain-robust: it
     spreads placements grid-wide, so it can never be zeroed by a hostile
     terrain layout the way a fixed coordinate list can (cf. the official
     Level 4 zero for the Level 1 calibration file).
  2. Simulates it with the calibrated engine (on an assumed all-soil world) to
     obtain a predicted local score. This is a prediction, not the official
     score; the official evaluator uses the hidden world file.
  3. Writes output/levelN/candidate-best/solution.json (evaluator format) and
     diagnostics.json.

Deterministic: identical inputs -> byte-identical solution.json.

The previous best-known artifacts under output/level1/calibration-01 and
output/level1/candidate-02 are NOT modified.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photospheria.data.loaders import load_challenge_data
from photospheria.levels.configs import LEVEL_CERTAINTY, level_config
from photospheria.simulation.full_engine import EngineAssumptions, Simulator
from photospheria.solver.balanced_fill import order_species_for_shade, plan_zoned_fill

STARTERS = ["Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree"]


def to_evaluator_json(actions_by_tick: dict[int, list[tuple[int, int, int]]]) -> dict:
    """Serialise to the official evaluator format: plant_index/row/col."""
    entries = []
    for tick in sorted(actions_by_tick):
        plants = [
            {"plant_index": idx, "row": row, "col": col}
            for (idx, row, col) in actions_by_tick[tick]
        ]
        entries.append({"tick": tick, "plants": plants})
    return {"actions": entries}


def build_for_level(level_id: int, data: dict) -> tuple[dict, dict]:
    config = level_config(level_id)
    plants = {p.plant: p for p in data["plants"]}
    species = order_species_for_shade([plants[n] for n in STARTERS])

    plan = plan_zoned_fill(config, species, coverage_fraction=1.0)
    solution = to_evaluator_json(plan.actions_by_tick)

    # Predicted score on an assumed all-soil world (both with and without spread
    # to bracket the outcome). Spread reflects an optimistic all-soil world;
    # no-spread reflects the guaranteed manual floor.
    def simulate(spread: bool):
        sim = Simulator(
            config, data["plants"], animals=data["animals"],
            classifications=data["classifications_mapping"],
            unlocks={u.plant: u.unlock for u in data["unlocks"]},
            assumptions=EngineAssumptions(spread_enabled=spread),
        )
        return sim.run(plan.actions_by_tick)

    floor = simulate(spread=False)
    with_spread = simulate(spread=True)

    diagnostics = {
        "level": level_id,
        "config_certainty": LEVEL_CERTAINTY[level_id],
        "grid": {"width": config.width, "height": config.height, "cmax": config.cmax,
                 "total_ticks": config.total_ticks},
        "strategy": "zoned balanced survival-window fill of the 5 guaranteed starter species",
        "survival_window": plan.survival_window,
        "zones": plan.zones,
        "total_actions": plan.total_actions(),
        "predicted_all_soil_no_spread": {
            "occupied_cells_C": floor.occupied_cells,
            "species_present": len(floor.species_counts),
            "entropy": floor.entropy,
            "main_score": floor.main_score,
            "longevity_score": floor.longevity_score,
            "final_score": floor.final_score,
            "leaderboard_score": floor.leaderboard_score,
            "species_counts": dict(sorted(floor.species_counts.items())),
        },
        "predicted_all_soil_with_spread": {
            "occupied_cells_C": with_spread.occupied_cells,
            "species_present": len(with_spread.species_counts),
            "entropy": with_spread.entropy,
            "main_score": with_spread.main_score,
            "longevity_score": with_spread.longevity_score,
            "final_score": with_spread.final_score,
            "leaderboard_score": with_spread.leaderboard_score,
            "species_counts": dict(sorted(with_spread.species_counts.items())),
        },
        "notes": [
            "alpha=1, k=1 calibrated exactly against the official Level 1 log.",
            "Scores are predictions on an assumed all-soil world; the official "
            "evaluator uses the hidden level terrain/soil/event file.",
            "The plan spreads placements grid-wide and only plants guaranteed "
            "species, so it degrades gracefully and cannot be zeroed by hostile "
            "terrain the way a fixed coordinate list can.",
        ],
    }
    return solution, diagnostics


def main() -> int:
    data = load_challenge_data()
    root = Path(__file__).resolve().parents[1]
    summary = []
    for level_id in (1, 2, 3, 4):
        solution, diagnostics = build_for_level(level_id, data)
        out_dir = root / "output" / f"level{level_id}" / "candidate-best"
        out_dir.mkdir(parents=True, exist_ok=True)
        sol_path = out_dir / "solution.json"
        diag_path = out_dir / "diagnostics.json"
        sol_text = json.dumps(solution, indent=2) + "\n"
        sol_path.write_text(sol_text, encoding="utf-8")
        diag_path.write_text(json.dumps(diagnostics, indent=2, default=str) + "\n", encoding="utf-8")
        sha = hashlib.sha256(sol_text.encode("utf-8")).hexdigest()
        floor = diagnostics["predicted_all_soil_no_spread"]["leaderboard_score"]
        spread = diagnostics["predicted_all_soil_with_spread"]["leaderboard_score"]
        summary.append((level_id, sol_path, sha, floor, spread))
        print(f"Level {level_id}: {sol_path}")
        print(f"  sha256={sha}")
        print(f"  predicted leaderboard: floor(no-spread)={floor:,}  with-spread={spread:,}")
    print("\nDone. Prior best-known artifacts were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
