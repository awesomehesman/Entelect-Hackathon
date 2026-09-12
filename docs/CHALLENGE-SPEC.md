# Challenge specification

## Objective

Build the best possible sample of Photospherian plant life for Earth scientists by maximising diversity while maintaining long-lived final-state plants. The official problem statement states the goal is to create a large and diverse sample and explicitly says the score is primarily determined by the number of different species present in the final sample. The final score combines a main diversity-and-coverage score with a secondary longevity score.

## Game structure

- The garden is an N × M grid.
- Each cell can contain one plant at a time unless an explicit rule allows coexistence.
- Time is discrete and represented with ticks.
- On each tick, the player may choose between zero and twenty planting actions.
- A planting action specifies the tick, the plant index, the row and the column.
- Only the final world state is used for scoring.
- The simulation is deterministic for a fixed world configuration and seed/state.

## Explicit actions

The submission is a JSON array of tick entries. Each tick contains a list of planting actions. The example in the official statement uses "plant_index" while the schema section shows "index". This discrepancy is recorded as HIGH PRIORITY validation in the submission documentation and the ambiguity log.

The problem statement also states:

- Coordinates must remain in grid bounds.
- Multiple plants may be planted during the same tick.
- Plant indices must match the plant catalogue.
- Plants with unlock conditions will only place successfully if all unlocks are met.
- Plants can only be placed in soil; non-soil terrain is uninhabitable.
- One plant per cell; if a plant is placed on an occupied cell, the existing plant is replaced.
- Up to 20 plants per tick; only the first 20 entries are planted.

## Tick semantics

The official PDF states that planting actions occur on ticks from 0 (initial setup) to T-1, with final actions on the penultimate day, and scoring on the final day. The PDF also contains a summary of environmental simulation states, but it does not provide a complete per-tick processing order. That ordering is treated as unresolved and is recorded in ASSUMPTIONS-AND-AMBIGUITIES.md.

## Planting limits

- Minimum 0 actions per tick.
- Maximum 20 explicit planting actions per tick.
- Only the first 20 actions in each tick list are processed.

## Initial unlocked plants

The game starts with access to exactly these five plants:

- Grass
- Rose Bush
- Lavender
- Dwarf Sunflower
- Oak Tree

## Locked plants

The plant catalogue contains 31 species total. The five species above are initially available. The other 26 species have explicit unlock conditions defined in plant_unlock_conditions.json.

## Replacement semantics

The problem statement says:

- Only one plant may be placed on a cell.
- If an action places a plant on an occupied cell, the existing plant is replaced by the new plant.
- This replacement is explicitly distinct from spread competition and special rules like coexistence.

## Soil restrictions

The soil types are numeric IDs:

- 0 = Dirt
- 1 = Mud
- 2 = Clay
- 3 = Burnt

The PDF notes that plants can only be placed on or spread into preferred soil types. It also notes that paths, stones, water features, cracks and burnt soil affect spread and survivability. Plants cannot spread onto paths; stone is uninhabitable; water is a feature surrounded by clay; cracked cells are special terrain; and burnt soil is harsh for almost all species.

## Final-state-only scoring

The official scoring function explicitly applies only to the final state of the garden on the final tick. Plants that died before the final tick contribute nothing to the score.

## Deterministic/reproducible requirement

The challenge requires deterministic and reproducible simulation and submission generation. The AGENTS instructions explicitly state that a valid solver must reproduce from source and behave deterministically for a fixed seed/configuration.

## Level progression

The problem statement defines four levels:

- Level 1: Greenhouse Study
- Level 2: Garden Growth Study
- Level 3: Park Potential
- Level 4: Forest

The official statement also says that the world can contain weather events, seasons, animals, soil types and varying terrain. The level files themselves are not present in the repository, so exact world configuration remains a blocker for exact simulation and final solution generation.

## Known supplied resources

The authoritative inputs present in this repository are:

- problem-statement.pdf
- plant_dataset.json
- plant_unlock_conditions.json
- animals.json
- classifications.json

## Missing resources

The repository does not contain any level/world files and no simulation code or solver implementation. No explicit world configuration, world events schedule, grid dimensions, T value, terrain layout, water/stone/path/crack layout, or level YAML/JSON was found.

This is a blocker for exact simulation and final solution generation.

## Dataset summary

- Total plant species: 31
- Initial plantable species: 5
- Locked species: 26
- Unlock definitions: 26
- Animal entries: 10
- Classification groups: 15
