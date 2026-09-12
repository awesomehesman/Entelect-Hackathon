# Architecture

The project uses one shared simulation and data foundation. Level modules provide configuration and evidence; they do not define alternate copies of generic gameplay mechanics.

## Shared Engine vs Level-Specific Configuration

### Shared

- datasets and shared data models
- world, cell, and plant-instance models
- coordinate validation
- planting and replacement contracts
- ageing and maturity
- spread geometry
- nutrient drain, death, and dead matter
- shade
- competition policy and ambiguity guards
- unlock conditions and condition evaluation
- classification resolution and ambiguity handling
- animals and events interfaces
- season transition algorithm
- scoring formulas
- candidate serialization and validation
- diagnostics and calibration record types

### Level-specific

- dimensions and tick limits
- terrain and soil data when supplied
- season, weather, and world-event schedules
- enabled systems
- initially unlocked species
- evaluator calibration observations
- confirmed submission field evidence
- strategy heuristics and candidate layouts

Level 1 uses `LevelConfig` values for its observed 50 x 50, 500-tick world, disabled animals/weather, observed season schedule, `alpha=1` evidence, and `plant_index` evidence. Levels 2-4 currently expose only the dimensions and explicitly supplied enabled-system facts; unknown schedules and terrain are left empty rather than invented.

The project must not maintain four independent simulators. A future engine should accept `LevelConfig` and datasets as inputs and use the same shared mechanics for every level.

## Compatibility boundary

`photospheria.simulation.level1` remains as a compatibility adapter for existing tests and commands. Its `World` subclasses the shared core world and delegates generic nutrient, shade, season, and geometry behavior. Its remaining content is Level 1 configuration compatibility and diagnostics, not a second generic engine.

## Calibration certainty

Evaluator-derived values live under `photospheria.calibration` with explicit statuses: observed, inferred, suspected, or unknown. Suspected `k=1` is not used as a global mechanic constant.
