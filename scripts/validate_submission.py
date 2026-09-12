#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from photospheria.submission.models import Submission, TickActions, PlantAction
from photospheria.submission.validator import validate_submission


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Photospheria submission JSON file.")
    parser.add_argument("path", nargs="?", help="Path to a submission JSON file.")
    parser.add_argument("--strict", action="store_true", help="Validate stronger constraints when a world context is available.")
    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        return 0

    p = Path(args.path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    submission = Submission.model_validate(payload)
    validate_submission(submission, strict=args.strict)
    print("Submission valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
