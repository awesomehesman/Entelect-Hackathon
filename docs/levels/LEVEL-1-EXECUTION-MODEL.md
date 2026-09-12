# Level 1 execution model

This document records what the official problem statement establishes about execution. It does not infer an evaluator implementation that the statement does not describe.

## Statements from the official PDF

| Statement                                                                                   | Source        | Classification                                               |
| ------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------ |
| The garden is an `N x M` grid and each cell is a coordinate location.                       | PDF p.2-3     | EXPLICIT                                                     |
| Time is discrete and represented with ticks.                                                | PDF p.2       | EXPLICIT                                                     |
| A submission is a sequence of planting instructions.                                        | PDF p.2-3     | EXPLICIT                                                     |
| Actions may be scheduled from tick `0` through `T-1`; scoring uses the final day.           | PDF p.3       | EXPLICIT                                                     |
| A JSON file contains the submitted solution.                                                | PDF p.4       | EXPLICIT                                                     |
| Each action identifies a plant index and row/column coordinates.                            | PDF p.4-5     | EXPLICIT                                                     |
| Coordinates must be within the grid.                                                        | PDF p.5       | EXPLICIT                                                     |
| At most 20 plants may be planted per tick; only the first 20 are planted.                   | PDF p.5       | EXPLICIT                                                     |
| Plant indices must match the supported plant catalogue.                                     | PDF p.5       | EXPLICIT                                                     |
| Locked plants are ignored until their unlock conditions are met.                            | PDF p.3, p.5  | EXPLICIT                                                     |
| An occupied cell is replaced by an explicit planting action.                                | PDF p.5       | EXPLICIT                                                     |
| Level 1 is a greenhouse that guards against animals and weather, while seasons still apply. | PDF p.10      | EXPLICIT                                                     |
| Level 1 uses a small subset of plants.                                                      | PDF p.10      | EXPLICIT, but the exact level subset is not enumerated there |
| Seasons are dictated by a level file containing season names and transition ticks.          | PDF p.8       | EXPLICIT                                                     |
| World events are scheduled at ticks defined in a level file.                                | PDF p.7       | EXPLICIT                                                     |
| Soil and terrain affect placement and spread.                                               | PDF p.5, p.7  | EXPLICIT                                                     |
| The five initial plants are Grass, Rose Bush, Lavender, Dwarf Sunflower, and Oak Tree.      | PDF p.6       | EXPLICIT                                                     |
| The final score is applied only to the final garden state.                                  | PDF p.3, p.10 | EXPLICIT                                                     |

## Execution questions not answered by the PDF

| Question                                                                           | Classification         | Evidence                                                                                              |
| ---------------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------- |
| Whether submitted source code is executed by the official evaluator                | UNKNOWN                | The PDF defines a JSON submission, but does not define source execution.                              |
| Whether the source ZIP participates in scoring or is used only for reproducibility | UNKNOWN                | No source-ZIP execution contract appears in the PDF.                                                  |
| Whether the evaluator internally constructs the world from hidden level data       | UNKNOWN                | The PDF refers to a level file, but the evaluator's ownership and delivery mechanism are unspecified. |
| Whether the submitted JSON alone drives the official simulation                    | IMPLIED                | The PDF says the solution is a JSON action schedule, but does not describe other runtime inputs.      |
| Whether level-specific data should be embedded in source code                      | UNKNOWN                | No embedding instruction appears in the PDF.                                                          |
| Whether soil/terrain are fixed or procedurally generated                           | UNKNOWN                | Soil and terrain are described, but no Level 1 layout or generator is supplied.                       |
| Whether a random seed exists or is supplied                                        | UNKNOWN                | No seed field or generation procedure is specified in the PDF.                                        |
| Whether seasons are globally defined or level-specific                             | IMPLIED level-specific | The PDF explicitly says season changes are dictated in the level file.                                |
| Whether all coordinates in a nominal 50 x 50 Level 1 world are usable soil         | UNKNOWN                | The PDF says non-soil terrain is uninhabitable; no Level 1 terrain layout is present.                 |
| Whether `plant_index` or `index` is the accepted action key                        | UNKNOWN                | The example uses `plant_index` on p.4; the schema uses `index` on p.5.                                |

## Local evidence result

The repository contains no Level 1 world file, soil grid, terrain map, season schedule, random seed, or evaluator/source-ZIP contract. The generic resource archive contains only the four JSON datasets. Therefore this project must not invent those values.
