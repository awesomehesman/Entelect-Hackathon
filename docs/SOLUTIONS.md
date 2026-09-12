# Best-known solutions

This document records the deterministic solver, the calibrated simulator it is
validated against, and the best-known valid solution generated for each level.

## Summary

Official results measured for the first (band-fill) submissions, and the
current (stripe) candidate predictions:

| Level | Grid | Ticks | Cmax | Band-fill official | Stripe predicted (optimistic) |
| ----- | ---- | ----- | ---- | ------------------ | ----------------------------- |
| 1 | 50×50 | 500 | 2,500 | 193,420,934 | 388,652,852 |
| 2 | 70×100 | 500 | 7,000 | 218,027,623 | 360,273,410 |
| 3 | 150×150 | 800 | 22,500 | 141,237,911 | 179,774,086 |
| 4 | 200×300 | 800 | 60,000 | 45,890,894 | 104,456,635 |

Stripe predictions are **local simulator estimates and are optimistic**: the
simulator's spread model diverges from the official evaluator (it overpredicted
Level 1 by ~1.75×). Treat them as an upper-ish bound. Even after discounting,
the stripe layout is expected to beat the band-fill official on every level
because it keeps entropy far higher.

### What the logs taught us

The band-fill submissions were scored by the official evaluator (logs under
`output/levelN/Logs/`). Three lessons:

1. **Manual placement on an already-occupied cell is DENIED** ("plant already
   occupies cell"), not applied as a replacement. This contradicts the PDF text
   but is the observed evaluator behaviour, and per AGENTS.md the verified
   evaluator outranks the problem statement.
2. **Uncontrolled spread monocultures the garden.** Every level collapsed to a
   Grass/Dwarf-Sunflower dominance with entropy ~0.29–0.32 (versus the 0.4687
   maximum), because interleaved bands let fast spreaders overrun neighbouring
   species and deny their placements.
3. **Level 2 is 70×100** (width 70, height 100), not 100×70.

## Scoring model (calibrated, exact)

Reproduced to full float precision against the official Level 1 log
(`SubmissionLogs/dfec4b87-…-evaluation.log`):

* `alpha = 1`, `k = 1`.
* `main = H · (C / Cmax)`, `H = −Σ pᵢ log₃₁ pᵢ`, `N = 31` species total.
* `longevity = Σ (lifespanᵢ / T) / Cmax` over cells occupied at the final tick.
* `final = 0.8 · main + 0.2 · longevity`.
* `leaderboard = round(final · 1e9)`.
* Lifespan of a plant present at final scoring = `(T − 1) − birth_tick + 1`
  (≥ 1). A plant survives to the final tick only if planted within the last
  ~100 ticks (nutrient capacity 100, drain 1/tick).

Regression guard: `tests/integration/test_engine_calibration.py` asserts the
engine reproduces every reported official statistic.

## Strategy — vertical stripes (spread containment)

The main score (80% weight) is `H · (C / Cmax)`. The band-fill submissions
proved that spread, not coverage, is the binding problem: it crushes entropy by
monoculturing the garden. The current plan (`src/photospheria/solver/stripe_fill.py`)
fixes this by **confining each species to its own full-height column stripe**:

* Each of the five starter species owns a contiguous vertical stripe of width
  `W // 5`. A species only borders two others along a single thin vertical seam,
  so spread stays mostly *inside* its own stripe — which is diversity-neutral
  (same species) and therefore does not lower entropy.
* All placements are scheduled inside the survival window (last ~99 ticks) so
  the manually placed cells are alive at the final tick.
* Placements are round-robin across species so each 20-action tick batch is
  balanced, and the plan places ~1,980 cells (the survival-window budget).

Because manual placement on an occupied cell is denied, keeping species in
separate stripes also avoids wasting the budget on placements that a spreader
has already claimed.

This plan is robust to unknown terrain: placements landing on non-soil are
simply ignored (reducing coverage, never invalidating the submission), and it
still plants only guaranteed species, so it cannot be zeroed the way a fixed
coordinate list can (cf. the original Level 4 zero).

### Known limitation

On the long levels (3 and 4, T = 800) the fast spreaders (Grass, Dwarf
Sunflower) still have ~99 ticks to cross the seam and encroach on neighbouring
stripes, so entropy is not fully preserved there. This is the main remaining
opportunity and would benefit from a more faithful spread model calibrated
against additional logs.

### Why only the five starter species

Level 1 has animals and weather disabled, so — confirmed by both the unlock
graph and the official log — **only the five starter species are reachable**.
For Levels 2–4 the locked species are gated behind animals, which require large
coverage/counts built up by spread; whether those thresholds are reached depends
on the hidden terrain. The guaranteed core is therefore the five starters. An
experimental two-phase unlock planner (`src/photospheria/solver/phased.py`)
reaches 11 species on an all-soil Level 2 (predicted ~460M) but halves the
guaranteed floor and depends on unverifiable spread/terrain/unlocks; it is kept
isolated and is **not** promoted until real terrain feedback is available.

## Reproduction

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e .[dev]

# calibrate the simulator against the official Level 1 log
python scripts/calibrate_engine.py         # prints CALIBRATION: PASS

# generate all four level solutions (deterministic)
python scripts/generate_solutions.py

# validate the evaluator format
python scripts/validate_evaluator_format.py output/level1/candidate-best/solution.json --width 50 --height 50 --ticks 500
python scripts/validate_evaluator_format.py output/level2/candidate-best/solution.json --width 70 --height 100 --ticks 500
python scripts/validate_evaluator_format.py output/level4/candidate-best/solution.json --width 200 --height 300 --ticks 800

# compare the simulator against the official logs
python scripts/compare_logs.py

python -m pytest -q                        # 46 passing
```

Outputs (deterministic SHA-256 of `solution.json`):

| Level | Path | SHA-256 |
| ----- | ---- | ------- |
| 1 | `output/level1/candidate-best/solution.json` | `6d7940acc36975aa5197c63913dc32beaa09879657e1a093a7e104791b90db5f` |
| 2 | `output/level2/candidate-best/solution.json` | `80de45d5ec9de22456326681ecaf73bf1ad995c1a6b8c3a5ec176dbc778aa25a` |
| 3 | `output/level3/candidate-best/solution.json` | `305ad5a87836ac454d8b3051faab81bc9ce0c48559a6cd3ae451e6a240fa9045` |
| 4 | `output/level4/candidate-best/solution.json` | `e9a035702b2b82ea90e9cf6e536feb80153693f68f915a47a1a81e81820561d0` |

## Known limitations and open items

* **Level terrain/soil/event files are not in the repository** (loaded
  server-side). Predicted scores assume all-soil; real coverage may be lower.
  Level 1, 2 and 4 dimensions/ticks are now confirmed from the official logs
  (Level 2 = 70×100); Level 3 dimensions and the season/event schedules for
  Levels 2–4 are still assumptions (see
  `src/photospheria/levels/configs.py` `LEVEL_CERTAINTY`).
* **The simulator's spread model diverges from the official evaluator.** It
  overpredicted Level 1 by ~1.75× and picks a different dominant spreader, so
  its absolute scores are optimistic. It is used for structural comparison, not
  precise scoring. `scripts/compare_logs.py` quantifies the gap.
* For large grids (Levels 3–4) the coverage term dominates and high scores rely
  on natural spread filling cells; the manual survival-window budget alone
  (1,980 cells) is small relative to Cmax. Containing the fast spreaders across
  stripe seams over 800 ticks is the main remaining opportunity.
* Several plant mechanics remain documented as unresolved (see
  `docs/ASSUMPTIONS-AND-AMBIGUITIES.md`); the engine handles them conservatively
  and never fabricates behaviour.
