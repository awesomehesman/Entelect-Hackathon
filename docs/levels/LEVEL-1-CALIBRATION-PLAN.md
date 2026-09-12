# Level 1 calibration plan

This is a minimal, non-executed plan. It is designed to answer high-value protocol questions with as few official submissions as possible. No submission is generated or sent by this repository.

| Candidate | Question                                                        | Structure                                                                                             | Possible outcomes                                        | Strategy impact                                                       | Cost/risk                                                              |
| --------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| A         | Which action field is accepted?                                 | One tick with one initial-species action using `plant_index` and the official example nesting         | Accepted, ignored, or schema error                       | Select serializer A or reject the example shape                       | One official submission; safest action still depends on hidden terrain |
| B         | Resolve `index` versus `plant_index` if A is inconclusive       | Structurally identical to A, using `index`                                                            | Accepted, ignored, or schema error                       | Select serializer B or retain unresolved dual support                 | One official submission; avoid if A gives a definitive schema result   |
| C         | Is an empty schedule valid?                                     | Empty action array using the confirmed outer schema                                                   | Accepted baseline or schema error                        | Establish no-action validity and final-state behavior                 | Lowest gameplay risk; consumes one submission                          |
| D         | Are the five initial species plantable at selected coordinates? | Five separated tick-0 actions, one per initial species, using confirmed schema                        | All accepted, some ignored, or coordinate/terrain errors | Distinguish coordinate validity from hidden terrain/soil restrictions | One submission; does not test spread                                   |
| E         | Do seasons materially affect Level 1?                           | A controlled pair differing only in early placement timing, after schema and world behavior are known | Different final state or identical state                 | Prioritize seasonal scheduling only if observable                     | Higher interpretation risk; defer until A-D                            |

## Protocol

1. Use only one candidate per official submission.
2. Start with A, then B only if necessary.
3. Do not submit an optimizer or a broad action schedule.
4. Preserve response logs and candidate hashes.
5. Update the simulator only from observed evaluator evidence, never from an ignored action interpreted as success.
