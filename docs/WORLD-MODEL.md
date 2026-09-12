# World model

This is the conceptual model that the future simulator will require. It intentionally describes only the state supported by the challenge source material and does not invent unsupported fields.

## World

Required state:

- width / height (N, M)
- tick count T
- grid cells
- current tick
- season schedule
- event schedule
- animal states
- unlock states
- global score state
- world state flags such as shade, dead matter, water, stone, path, cracks, burnt soil

## Cell

Required state:

- row, col
- soil type
- terrain flags (path, stone, water, crack, burnt soil)
- nutrients (0..100)
- dead_matter flag
- shade flag
- plant instance or null
- subsurface plant or null
- birth tick / age tracking

## PlantInstance

Required state:

- species index or species name
- row, col
- birth tick
- maturity tick or age
- alive flag
- lifespan cumulative ticks
- root type
- invasiveness rank
- planted manually or spread-generated
- current state flags for special rules

## SubsurfacePlant

Required state:

- species identity
- row, col
- alive flag
- owner cell reference
- promotion eligibility state

## SpeciesDefinition

Required state:

- plant name
- index
- preferred_soil
- growth parameters (time_to_maturity, spread_rate, spread_mechanism, spread_type, spread_range, root_type, invasiveness_rank)
- weaknesses
- special rules
- role
- unlock condition tree
- conditional modifiers

## AnimalState

Required state:

- id
- name
- present flag
- requirement evaluation result
- active effects

## Season

Required state:

- name
- tick transition

## WorldEvent

Required state:

- event name
- scheduled tick
- active flag
- transpired flag

## UnlockState

Required state:

- plant name
- unlocked flag
- condition tree result
- last evaluated tick

## Action

Required state:

- tick
- plant index
- row
- col
- validation status
- applied or ignored flag
- reason if ignored

## TickState

Required state:

- tick number
- actions applied
- spread events
- maturity updates
- environmental updates
- animal evaluation
- unlock evaluation
- score snapshot

## ScoreState

Required state:

- final counts by species
- total occupied cells
- diversity entropy H
- coverage factor
- longevity aggregate
- final score
- hidden calibration parameters alpha and k if used in empirical calibration
