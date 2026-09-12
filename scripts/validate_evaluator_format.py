#!/usr/bin/env python3
"""Validate a submission file against the OFFICIAL evaluator JSON format.

This matches the format the official evaluator accepted for Level 1 (see
SubmissionLogs/ and problem-statement.pdf p.4): a top-level object with an
"actions" array; each entry has an integer "tick" and a "plants" list; each
plant has "plant_index", "row", "col".

Constraints enforced (from PDF "Constraints" section):
* tick is an integer in 0..T-1 (T optional; if omitted only non-negativity).
* at most 20 plants per tick (only the first 20 would be planted; we warn if >20).
* coordinates non-negative and within width/height when supplied.
* plant_index is a known catalogue index when a catalogue is supplied.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photospheria.data.loaders import load_challenge_data


def validate(payload: dict, *, width: int | None, height: int | None, total_ticks: int | None,
             plant_indices: set[int] | None) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict) or "actions" not in payload:
        return ["Top-level must be an object containing an 'actions' array."]
    actions = payload["actions"]
    if not isinstance(actions, list):
        return ["'actions' must be a list."]
    seen_ticks: set[int] = set()
    for entry in actions:
        if not isinstance(entry, dict) or "tick" not in entry or "plants" not in entry:
            errors.append(f"Each action entry needs 'tick' and 'plants': {entry!r}")
            continue
        tick = entry["tick"]
        if not isinstance(tick, int) or tick < 0:
            errors.append(f"tick must be a non-negative integer: {tick!r}")
        if total_ticks is not None and isinstance(tick, int) and tick >= total_ticks:
            errors.append(f"tick {tick} is outside 0..{total_ticks - 1}")
        if tick in seen_ticks:
            errors.append(f"duplicate tick entry: {tick}")
        seen_ticks.add(tick)
        plants = entry["plants"]
        if not isinstance(plants, list):
            errors.append(f"'plants' must be a list on tick {tick}")
            continue
        if len(plants) > 20:
            errors.append(f"tick {tick} has {len(plants)} plants (>20; only first 20 would be planted)")
        for p in plants:
            if not isinstance(p, dict) or "plant_index" not in p or "row" not in p or "col" not in p:
                errors.append(f"plant needs plant_index/row/col on tick {tick}: {p!r}")
                continue
            idx, row, col = p["plant_index"], p["row"], p["col"]
            if plant_indices is not None and idx not in plant_indices:
                errors.append(f"unknown plant_index {idx} on tick {tick}")
            if not isinstance(row, int) or not isinstance(col, int) or row < 0 or col < 0:
                errors.append(f"row/col must be non-negative integers on tick {tick}: ({row},{col})")
                continue
            if height is not None and row >= height:
                errors.append(f"row {row} out of bounds (height {height}) on tick {tick}")
            if width is not None and col >= width:
                errors.append(f"col {col} out of bounds (width {width}) on tick {tick}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--ticks", type=int)
    args = ap.parse_args()

    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    data = load_challenge_data()
    plant_indices = {p.index for p in data["plants"]}
    errors = validate(payload, width=args.width, height=args.height, total_ticks=args.ticks,
                      plant_indices=plant_indices)
    if errors:
        print("INVALID:")
        for e in errors:
            print("  -", e)
        return 1
    total = sum(len(e["plants"]) for e in payload["actions"])
    print(f"VALID: {len(payload['actions'])} tick entries, {total} plant actions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
