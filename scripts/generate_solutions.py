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
  3. Writes output/levelN/candidate-best/solution.json (evaluator format),
     diagnostics.json, and a reproducible source.zip.

Each candidate-best directory mirrors the reference calibration-01 layout:
both a solution.json (upload for scoring) and a source.zip (reproducible
source bundle) are produced, ready to upload to the portal.

Deterministic: identical inputs -> byte-identical solution.json and a
byte-stable source.zip (fixed timestamps, sorted entries).

The previous best-known artifacts under output/level1/calibration-01 and
output/level1/candidate-02 are NOT modified.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photospheria.data.loaders import load_challenge_data
from photospheria.levels.configs import LEVEL_CERTAINTY, level_config
from photospheria.simulation.full_engine import EngineAssumptions, Simulator
from photospheria.solver.stripe_fill import plan_stripe_fill

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
    species = [plants[n] for n in STARTERS]

    plan = plan_stripe_fill(config, species)
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
        "strategy": "vertical-stripe balanced survival-window fill of the 5 "
                    "guaranteed starter species (spread-containment)",
        "survival_window": plan.survival_window,
        "stripes": plan.stripes,
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
            "Manual placement on an occupied cell is DENIED (observed in the "
            "official logs), so each species is confined to its own vertical "
            "stripe; spread stays mostly within a stripe (diversity-neutral), "
            "keeping entropy far higher than the previously submitted band "
            "layout (which monocultured to entropy ~0.32).",
            "Scores are local-simulator predictions and are optimistic: the "
            "simulator's spread model diverges from the official evaluator "
            "(observed ~1.75x overprediction on Level 1). Treat them as an "
            "upper-ish bound, not the official score.",
        ],
    }
    return solution, diagnostics


# Individual files (data, scripts, project config) bundled into every source.zip.
SOURCE_BUNDLE_FILES = [
    "Artifacts/additional-resources/plant_dataset.json",
    "Artifacts/additional-resources/plant_unlock_conditions.json",
    "Artifacts/additional-resources/animals.json",
    "Artifacts/additional-resources/classifications.json",
    "scripts/generate_solutions.py",
    "scripts/calibrate_engine.py",
    "scripts/validate_evaluator_format.py",
    "pyproject.toml",
]

# The entire package tree is bundled recursively so the import graph resolves
# cleanly regardless of internal __init__ import chains.
SOURCE_BUNDLE_TREES = [
    "src/photospheria",
]

# Fixed timestamp for byte-stable, reproducible archives.
_ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def _bundle_paths(root: Path) -> list[str]:
    paths: list[str] = list(SOURCE_BUNDLE_FILES)
    for tree in SOURCE_BUNDLE_TREES:
        base = root / tree
        for p in base.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            paths.append(str(p.relative_to(root)))
    return sorted(set(paths))


def _level_readme(level_id: int, diagnostics: dict, sha: str) -> str:
    g = diagnostics["grid"]
    floor = diagnostics["predicted_all_soil_no_spread"]
    spread = diagnostics["predicted_all_soil_with_spread"]
    return f"""# Photospheria Level {level_id} — candidate-best

Reproducible source bundle for the Level {level_id} submission.

## Reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e .
python scripts/generate_solutions.py
```

This regenerates `output/level{level_id}/candidate-best/solution.json`.

Expected `solution.json` SHA-256:

    {sha}

## What this solution is

Strategy: {diagnostics['strategy']}.

- Grid: {g['width']}x{g['height']} (Cmax={g['cmax']}), {g['total_ticks']} ticks.
- Survival window (ticks): {diagnostics['survival_window']}.
- Explicit plant actions: {diagnostics['total_actions']}.
- Species: the five guaranteed starter species (Grass, Rose Bush, Lavender,
  Dwarf Sunflower, Oak Tree).

Predicted leaderboard score (local simulator, assumed all-soil world; NOT the
official score):

- floor (no natural spread): {floor['leaderboard_score']:,}
- with natural spread:       {spread['leaderboard_score']:,}

The scoring model (alpha=1, k=1) is calibrated to reproduce the official
Level 1 evaluation log to full float precision. The submitted `solution.json`
is what the portal scores; this source bundle documents how it was produced.
"""


def build_source_zip(zip_path: Path, root: Path, level_id: int, diagnostics: dict,
                     solution_text: str, sha: str) -> None:
    readme = _level_readme(level_id, diagnostics, sha)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # README + the produced solution.json, then the source chain (sorted).
        zf.writestr(zipfile.ZipInfo("README.md", date_time=_ZIP_DATE), readme)
        zf.writestr(zipfile.ZipInfo("solution.json", date_time=_ZIP_DATE), solution_text)
        for rel in _bundle_paths(root):
            src = root / rel
            if not src.exists():
                continue
            info = zipfile.ZipInfo(rel, date_time=_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, src.read_bytes())


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
        zip_path = out_dir / "source.zip"
        sol_text = json.dumps(solution, indent=2) + "\n"
        sol_path.write_text(sol_text, encoding="utf-8")
        diag_path.write_text(json.dumps(diagnostics, indent=2, default=str) + "\n", encoding="utf-8")
        sha = hashlib.sha256(sol_text.encode("utf-8")).hexdigest()
        build_source_zip(zip_path, root, level_id, diagnostics, sol_text, sha)
        floor = diagnostics["predicted_all_soil_no_spread"]["leaderboard_score"]
        spread = diagnostics["predicted_all_soil_with_spread"]["leaderboard_score"]
        summary.append((level_id, sol_path, sha, floor, spread))
        print(f"Level {level_id}: {out_dir}")
        print(f"  solution.json sha256={sha}")
        print(f"  source.zip -> {zip_path.name}")
        print(f"  predicted leaderboard: floor(no-spread)={floor:,}  with-spread={spread:,}")
    print("\nEach candidate-best dir now has solution.json + source.zip (upload both).")
    print("Prior best-known artifacts were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
