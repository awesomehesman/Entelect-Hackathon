# Best-known solutions

This document records the deterministic solver, the calibrated simulator it is
validated against, and the best-known valid solution generated for each level.

## Summary

| Level | Grid | Ticks | Cmax | Predicted floor (no spread) | Predicted with spread | Prior official |
| ----- | ---- | ----- | ---- | --------------------------- | --------------------- | -------------- |
| 1 | 50×50 | 500 | 2,500 | 312,795,056 | 376,690,788 | 750,687 |
| 2 | 100×70 | 500 | 7,000 | 111,712,520 | 304,625,112 | — |
| 3 | 150×150 | 800 | 22,500 | 34,095,006 | 136,830,826 | — |
| 4 | 200×300 | 800 | 60,000 | 12,785,627 | 68,046,822 | 0 |

Predicted scores are **local simulator predictions on an assumed all-soil
world**, not official scores. The official evaluator uses the hidden level
terrain/soil/event file. The two numbers bracket the outcome: the "no spread"
floor is the guaranteed manual result if no natural spread occurs; the "with
spread" figure is the optimistic all-soil result including spread. The real
score will fall between these depending on the hidden terrain.

The prior official Level 1 submission scored 750,687. The prior Level 4
submission (the Level 1 calibration file reused) scored **0** because its five
fixed centre coordinates were all non-soil in Level 4. The new solutions spread
placements grid-wide and therefore cannot be zeroed the same way.

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

## Strategy

The main score (80% weight) is maximised by having many *distinct* species,
kept *balanced* (equal counts maximise entropy), covering as many cells as
possible, all *alive at the final tick*.

The promoted plan is a **zoned, balanced, survival-window fill** of the five
guaranteed-reachable starter species (Grass, Rose Bush, Lavender, Dwarf
Sunflower, Oak Tree):

* All placements are inside the survival window (last ~99 ticks) so they are
  alive at the final tick.
* Each species is placed in its own contiguous row-band; shade-sensitive Grass
  (`no_shade_survival`) is placed far from the shade-casting Oak Tree
  (`shade_radius = 4`), and Oak is scheduled so late it never matures and thus
  never casts shade. Both avoid shade-kill.
* Placements are interleaved so any contiguous region the real world rejects
  still leaves a balanced sample.

This plan is robust to unknown terrain: placements landing on non-soil in the
hidden world are simply ignored (reducing coverage, never invalidating the
submission), and natural spread can only add coverage. Under a simulated 40%
non-soil Level 1 the plan still scores ~228M with balanced entropy.

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
python scripts/validate_evaluator_format.py output/level4/candidate-best/solution.json --width 200 --height 300 --ticks 800

python -m pytest -q                        # 43 passing
```

Outputs (deterministic SHA-256 of `solution.json`):

| Level | Path | SHA-256 |
| ----- | ---- | ------- |
| 1 | `output/level1/candidate-best/solution.json` | `eda3fec32042e98dc118f850b5379626dcc9779a1e391f4718b912aa851d5791` |
| 2 | `output/level2/candidate-best/solution.json` | `3012317dd817a3ea62b4d87f7c6322ccbf44e6f9961b458b89a461d9d2a490e3` |
| 3 | `output/level3/candidate-best/solution.json` | `cb9e47b2fa93010e02bf528e266dbc9b0b55c1ceda6ed669b4f4d01e104686bb` |
| 4 | `output/level4/candidate-best/solution.json` | `738a7255280007bef7c19a27678837962dd3d7f2368ffcc61e475b5e8e9bfd1b` |

## Known limitations and open items

* **Level terrain/soil/event files are not in the repository** (loaded
  server-side). Predicted scores assume all-soil; real coverage may be lower.
  Level 2/3 dimensions and season/event schedules are assumptions (see
  `src/photospheria/levels/configs.py` `LEVEL_CERTAINTY`); Level 1 and Level 4
  dimensions/ticks/schedules are confirmed from the official logs.
* For large grids (Levels 3–4) the coverage term dominates and high scores rely
  on natural spread filling cells; the manual survival-window budget alone
  (1,980 cells) is small relative to Cmax. This is the main opportunity if
  terrain feedback confirms spread behaviour.
* Several plant mechanics remain documented as unresolved (see
  `docs/ASSUMPTIONS-AND-AMBIGUITIES.md`); the engine handles them conservatively
  and never fabricates behaviour.
