# Validation plan

This validation plan defines future tests before implementation. It deliberately covers both unit-level correctness and differential/empirical checks against official benchmark behavior.

## Unit tests

- coordinate bounds
- 20-action limit per tick
- plant availability and unlock gating
- preferred soil restrictions
- replacement semantics on occupied cells
- maturity progression
- every spread geometry (VonNeumann, Moore, Row, Column, CrossHatch)
- spread cadence and spread-rate modifiers
- invasiveness order resolution
- shade state generation and consumption
- nutrient depletion and regeneration
- dead matter effects
- animals presence and dissipation
- AND/OR/NOT unlock trees
- coverage and count-based unlocks
- event-triggered unlocks
- feature_count semantics
- species_present and species_absent logic
- every special rule
- every weakness type
- coexistence behavior
- subsurface promotion
- world events and seasonal modifiers

## Differential and empirical validation

- compare simulation output against official challenge examples where available
- compare local simulator metrics with known final-score formula relationships
- test large balanced and unbalanced final states to verify entropy and score behavior
- verify that dead plants before final tick do not contribute to scoring
- run calibration sweeps over hidden alpha and k values to understand ranking effects
- validate that the simulator remains deterministic for fixed input configuration
- test candidate schedules under both initial-seed and no-event conditions where possible
- check that unlocks, animals and world events remain consistent in relation to each other
- confirm that the implementation does not silently normalize conflicting exact-string group names

## Required high-risk checks

- feature_count value semantics for fractional thresholds
- plant_index versus index field handling
- exact order of event/animal/unlock evaluation
- exact collision handling for overlapping spread results
- coexistence and subsurface plant counting
- crack generation and Skyvine traversal
- exact state transitions for dead matter and nutrient restoration
