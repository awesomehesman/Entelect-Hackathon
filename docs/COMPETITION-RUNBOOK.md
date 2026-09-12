# Competition runbook

## Live process

1. Never submit an unvalidated file.
2. Keep the current-best submission immutable.
3. Record each official submission with timestamp, git SHA, strategy, local metrics, leaderboard score and notes.
4. Treat leaderboard results as information about hidden scoring parameters.
5. Avoid wasteful repeated submissions.
6. Submit only when validity confidence is high and the candidate materially improves expected results or is intentionally created as a calibration experiment.

## Results table

Official results (from SubmissionLogs/ and output/levelN/Logs/):

| Attempt | Level | Grid | Strategy | C | Entropy | Official Score |
| --- | --- | --- | --- | --- | --- | --- |
| cal01 | 1 | 50x50 | 5 plants @ tick 499 (calibration) | 5 | 0.4687 | 750,687 |
| cal01 | 4 | 200x300 | reused L1 calibration file | 0 | 0.0 | 0 (centre non-soil) |
| band-fill | 1 | 50x50 | zoned band fill (5 starters) | 1793 | 0.322 | 193,420,934 |
| band-fill | 2 | 70x100 | zoned band fill (5 starters) | 5700 | 0.317 | 218,027,623 |
| band-fill | 3 | 150x150 | zoned band fill (5 starters) | 11858 | 0.320 | 141,237,911 |
| band-fill | 4 | 200x300 | zoned band fill (5 starters) | 11347 | 0.288 | 45,890,894 |

Lessons from the band-fill submissions: uncontrolled spread collapsed every
level to a Grass/Dwarf-Sunflower monoculture (entropy ~0.29-0.32), and manual
placement on an already-occupied cell is DENIED. Level 2 is 70x100 (not 100x70).

Current best-known candidates use the vertical-stripe spread-containment layout
(each species confined to its own column stripe so spread stays diversity-
neutral). Local-simulator predictions (optimistic; the sim overpredicted L1 by
~1.75x, so discount accordingly):

| Candidate | Level | Grid | Predicted with-spread (optimistic) | Beats current official? |
| --- | --- | --- | --- | --- |
| candidate-best | 1 | 50x50 | 388,652,852 | yes (>193M) |
| candidate-best | 2 | 70x100 | 360,273,410 | yes (>218M) |
| candidate-best | 3 | 150x150 | 179,774,086 | yes (>141M) |
| candidate-best | 4 | 200x300 | 104,456,635 | yes (>46M) |

Reproduce with `python scripts/generate_solutions.py`. Compare the sim to the
official logs with `python scripts/compare_logs.py`.
