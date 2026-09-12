# Competition runbook

## Live process

1. Never submit an unvalidated file.
2. Keep the current-best submission immutable.
3. Record each official submission with timestamp, git SHA, strategy, local metrics, leaderboard score and notes.
4. Treat leaderboard results as information about hidden scoring parameters.
5. Avoid wasteful repeated submissions.
6. Submit only when validity confidence is high and the candidate materially improves expected results or is intentionally created as a calibration experiment.

## Results table

Official (from SubmissionLogs/):

| Attempt | Level | Strategy | Species | C | Entropy | Official Score | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L1-cal01 | 1 | 5 plants @ tick 499 (calibration) | 5 | 5 | 0.4687 | 750,687 | Calibrated alpha=1, k=1 |
| L4-cal01 | 4 | reused L1 calibration file | 0 | 0 | 0.0 | 0 | Centre coords non-soil in L4 |

Best-known candidates (local simulator predictions on assumed all-soil world;
see docs/SOLUTIONS.md). Not yet submitted to the official evaluator.

| Candidate | Level | Strategy | Predicted floor (no spread) | Predicted with spread |
| --- | --- | --- | --- | --- |
| candidate-best | 1 | zoned balanced survival-window fill (5 starters) | 312,795,056 | 376,690,788 |
| candidate-best | 2 | zoned balanced survival-window fill (5 starters) | 111,712,520 | 304,625,112 |
| candidate-best | 3 | zoned balanced survival-window fill (5 starters) | 34,095,006 | 136,830,826 |
| candidate-best | 4 | zoned balanced survival-window fill (5 starters) | 12,785,627 | 68,046,822 |

Reproduce with `python scripts/generate_solutions.py`. Predicted scores bracket
the real outcome; the official evaluator uses the hidden level terrain file.
