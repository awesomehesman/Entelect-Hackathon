# Photospheria simulator foundation

## Mission

This repository is implementing the deterministic simulation foundation for the Entelect Hack<IT> "Root Cause Analysis" challenge without solving the optimisation problem yet.

## Authoritative resources

The source data used by the project must come from the challenge resources under:

- Artifacts/additional-resources/problem-statement.pdf
- Artifacts/additional-resources/plant_dataset.json
- Artifacts/additional-resources/plant_unlock_conditions.json
- Artifacts/additional-resources/animals.json
- Artifacts/additional-resources/classifications.json

No official challenge resource may be modified.

## Repository structure

- src/photospheria/ — simulation foundation code
- tests/ — unit and integration tests
- scripts/ — audit and validation utilities
- docs/ — challenge and implementation documentation

## Environment setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Running tests

```bash
python -m pytest -q
```

## Running the data audit

```bash
python scripts/audit_data.py
```

## Validating submissions

```bash
python scripts/validate_submission.py --help
```

## Current implementation phase

This repository is in PHASE 1: simulator foundation and framework validation.

## Known blockers

- Level/world files are missing from the repository.
- Exact world layout and event schedule cannot be loaded yet.
- Some challenge semantics are documented as unresolved and are intentionally isolated behind explicit interfaces.

## Important rule

DO NOT GENERATE A COMPETITION SUBMISSION UNTIL THE OFFICIAL LEVEL DATA HAS BEEN LOADED AND THE SIMULATOR HAS PASSED VALIDATION.
