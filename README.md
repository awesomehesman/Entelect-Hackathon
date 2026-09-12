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

## Level 1 — Reproducing the Submitted Solution

### Requirements

- Python 3
- No third-party Python dependencies are required for the calibration generator.

### Reproduction

From the extracted source ZIP root, run:

```bash
python3 scripts/generate_level1_calibration.py
```

This generates:

```text
output/level1/calibration-01/solution.json
```

### Expected SHA-256

The generated `solution.json` must have SHA-256:

```text
265ff402ff7e094fa7b5944d4a9e881cbf45ef340befbfeb1f401974d05428f7
```

Verify on macOS or Linux with:

```bash
shasum -a 256 output/level1/calibration-01/solution.json
```

On Linux, this alternative is also available:

```bash
sha256sum output/level1/calibration-01/solution.json
```

### Expected candidate

Calibration 01 deterministically creates:

- Level: 1
- Tick: 499
- Explicit plant actions: 5
- Serialization field: `plant_index`
- Species: Grass, Rose Bush, Lavender, Dwarf Sunflower, and Oak Tree

Species indices are resolved from the supplied official `plant_dataset.json`; they are not independently invented by the generator.

### Repository structure

```text
scripts/generate_level1_calibration.py
	Deterministically generates the submitted JSON.

Artifacts/additional-resources/plant_dataset.json
	Official challenge plant dataset used to resolve plant indices.

src/photospheria/levels/level1.py
	Level 1 constraints and validation used by the generator.

output/level1/calibration-01/solution.json
	Generated submission artifact.
```

### Determinism

Running the reproduction command multiple times with the same included source and dataset produces byte-identical `solution.json` output.

This reproduces the exact submitted JSON. It does not reproduce or claim the official leaderboard score; the official challenge evaluator calculates that score.

## Level 1 Candidate 02 — Reproduction

Candidate 02 is a local, unsubmitted calibration candidate. It uses 1,980 explicit placements in five survival-safe spatial zones and does not claim an official score.

From the extracted source ZIP root, run:

```bash
python3 scripts/generate_level1_candidate2.py
```

This generates:

```text
output/level1/candidate-02/solution.json
output/level1/candidate-02/diagnostics.json
```

The expected `solution.json` SHA-256 is:

```text
c27cb507a24584c557c5f0a0cde6d3d33e9bfdd3b222639bb45964ade204528e
```

The command reproduces the exact candidate JSON. It does not reproduce or claim the official evaluator score.

## Known blockers

- Level/world files are missing from the repository.
- Exact world layout and event schedule cannot be loaded yet.
- Some challenge semantics are documented as unresolved and are intentionally isolated behind explicit interfaces.

## Important rule

DO NOT GENERATE A FINAL COMPETITION SUBMISSION UNTIL THE OFFICIAL LEVEL DATA HAS BEEN LOADED AND THE SIMULATOR HAS PASSED VALIDATION.
