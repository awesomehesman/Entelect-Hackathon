#!/usr/bin/env python3
"""Compare the calibrated simulator against the official evaluation logs.

Runs each submitted solution.json through the simulator (with the confirmed
level config) and prints simulator vs official C / entropy / score, so we can
see how faithfully the spread model reproduces reality.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photospheria.data.loaders import load_challenge_data
from photospheria.levels.configs import level_config
from photospheria.simulation.full_engine import EngineAssumptions, Simulator

ROOT = Path(__file__).resolve().parents[1]


def parse_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"loaded level \((\d+)x(\d+), (\d+) ticks\)", text)
    grid = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    stat = re.search(r"PlantSim statistics: (\{.*)", text, re.DOTALL)
    stats = {}
    if stat:
        blob = stat.group(1)
        for key in ("score", "main_score", "longevity_score", "entropy",
                    "total_plants_planted_C", "density_factor", "c_max_or_grid_size"):
            mm = re.search(rf"'{key}': ([0-9.eE+-]+)", blob)
            if mm:
                stats[key] = float(mm.group(1))
        counts = re.search(r"'plant_counts': array\(\[([^\]]+)\]", blob, re.DOTALL)
        if counts:
            nums = [float(x) for x in re.findall(r"[0-9.]+", counts.group(1))]
            stats["plant_counts"] = nums
    setscore = re.search(r"Setting score to (\d+)", text)
    if setscore:
        stats["leaderboard"] = int(setscore.group(1))
    return {"grid": grid, "stats": stats}


def main() -> int:
    data = load_challenge_data()
    for level_id in (1, 2, 3, 4):
        logs = list((ROOT / "output" / f"level{level_id}" / "Logs").glob("*.log"))
        sol_path = ROOT / "output" / f"level{level_id}" / "candidate-best" / "solution.json"
        if not logs or not sol_path.exists():
            continue
        info = parse_log(logs[0])
        sol = json.loads(sol_path.read_text())
        acts = {e["tick"]: [(p["plant_index"], p["row"], p["col"]) for p in e["plants"]]
                for e in sol["actions"]}
        cfg = level_config(level_id)
        sim = Simulator(cfg, data["plants"], animals=data["animals"],
                        classifications=data["classifications_mapping"],
                        unlocks={u.plant: u.unlock for u in data["unlocks"]},
                        assumptions=EngineAssumptions(spread_enabled=True))
        r = sim.run(acts)
        o = info["stats"]
        print(f"=== Level {level_id}  (log grid {info['grid']}, cfg {cfg.width}x{cfg.height}) ===")
        print(f"  {'metric':12} {'official':>16} {'simulator':>16}")
        print(f"  {'C':12} {o.get('total_plants_planted_C',0):>16.0f} {r.occupied_cells:>16}")
        print(f"  {'entropy':12} {o.get('entropy',0):>16.4f} {r.entropy:>16.4f}")
        print(f"  {'density':12} {o.get('density_factor',0):>16.4f} {r.density_factor:>16.4f}")
        print(f"  {'leaderboard':12} {o.get('leaderboard',0):>16.0f} {r.leaderboard_score:>16}")
        print(f"  official counts: {o.get('plant_counts')}")
        print(f"  sim counts:      {dict(sorted(r.species_counts.items()))}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
