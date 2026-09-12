#!/usr/bin/env python3
"""Calibrate the full engine against the official Level 1 evaluation log.

Official Level 1 statistics (SubmissionLogs/dfec4b87-...-evaluation.log):
    score                 = 0.000750686504099727
    main_score            = 0.0009373581301246587
    longevity_score       = 4e-06
    entropy               = 0.4686790650623293
    total_plants_planted_C= 5
    density_factor        = 0.002
    Cmax                  = 2500
    leaderboard           = 750687

Five plants (Grass, Rose Bush, Lavender, Dwarf Sunflower, Oak Tree) placed at
tick 499 near the centre; all survive to the final tick.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photospheria.data.loaders import load_challenge_data
from photospheria.simulation.full_engine import Simulator, WorldConfig

LEVEL1_SEASONS = ((0, "Spring"), (100, "Summer"), (200, "Autumn"), (300, "Winter"), (400, "Spring"))

EXPECTED = {
    "score": 0.000750686504099727,
    "main_score": 0.0009373581301246587,
    "longevity_score": 4e-06,
    "entropy": 0.4686790650623293,
    "density_factor": 0.002,
    "total_plants_planted_C": 5,
    "c_max_or_grid_size": 2500,
    "leaderboard_score": 750687,
}


def main() -> int:
    data = load_challenge_data()
    plants = data["plants"]
    idx = {p.plant: p.index for p in plants}
    config = WorldConfig(
        level_id=1, width=50, height=50, total_ticks=500,
        seasons_enabled=True, animals_enabled=False, weather_enabled=False,
        season_schedule=LEVEL1_SEASONS,
    )
    sim = Simulator(config, plants, animals=data["animals"],
                    classifications=data["classifications_mapping"],
                    unlocks={u.plant: u.unlock for u in data["unlocks"]})
    actions = {499: [
        (idx["Grass"], 25, 25),
        (idx["Rose Bush"], 25, 26),
        (idx["Lavender"], 26, 25),
        (idx["Dwarf Sunflower"], 26, 26),
        (idx["Oak Tree"], 24, 25),
    ]}
    result = sim.run(actions)
    got = result.as_dict()

    ok = True
    print("field                     expected                 got")
    for key, exp in EXPECTED.items():
        val = got[key]
        match = abs(val - exp) < 1e-12 if isinstance(exp, float) else val == exp
        ok = ok and match
        print(f"{key:24} {exp!r:24} {val!r:24} {'OK' if match else 'MISMATCH'}")
    print()
    print(json.dumps(got, indent=2, default=str))
    print()
    print("CALIBRATION:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
