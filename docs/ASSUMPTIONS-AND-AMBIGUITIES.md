# Assumptions and ambiguities

This file records unresolved questions and contradictions from the challenge data. All issues are explicitly marked with one of: RESOLVED, LIKELY, UNKNOWN, or BLOCKING.

## AMB-001 — Submission key discrepancy: "plant_index" vs "index"

- Status: OFFICIALLY OBSERVED FOR LEVEL 1; GENERIC DISCREPANCY REMAINS
- Conflict: The example submission uses "plant_index" while the schema section uses "index".
- Evidence: problem-statement.pdf shows example with plant_index; later schema says index.
- Resolution: The official Level 1 evaluator accepted `plant_index` in Calibration 01. Generic support for `index` remains because the PDF schema still shows both names and no Level 2-4 evidence exists.

## AMB-002 — Classification naming discrepancy

- Status: BLOCKING
- Conflict: animals.json uses "Shallow-root Species" while classifications.json defines "Shallowroot Species".
- Evidence: animals.json requirement on Virexids uses target "Shallow-root Species"; classifications.json defines "Shallowroot Species". This exact-string mismatch is not normalized by the raw source data.
- Resolution: Unresolved until higher-authority source confirms the canonical group name.

## AMB-003 — Glowcap Fungus unlock uses feature_count(dead_matter) with value 0.05

- Status: UNKNOWN
- Conflict: The problem statement defines feature_count as an absolute count of cells with a world feature, but the unlock uses 0.05 as a value.
- Evidence: unlock file uses {"type": "feature_count", "feature": "dead_matter", "operator": ">", "value": 0.05}; PDF says feature_count checks how many cells have a specific world feature.
- Resolution: This is an unresolved semantic discrepancy. It may mean percentage of world cells or it may be a scaling error in the source data; no silent assumption is allowed.

## AMB-004 — Exact tick processing order

- Status: UNKNOWN
- Conflict: The problem statement lists multiple per-tick concepts but does not provide a definitive order for the full simulation lifecycle.
- Evidence: the challenge text mentions planting, maturity, spread, environmental effects, animals, unlock evaluation, nutrient consumption, death, events, and scoring as distinct concerns, but not their exact ordering.
- Resolution: The simulator must validate the order empirically before being trusted.

## AMB-005 — Whether unlocks are permanent after first activation

- Status: UNKNOWN
- Conflict: The challenge states unlock conditions are checked before a plant can be placed, but it does not say whether a once-unlocked plant remains available forever or whether it must be periodically revalidated.
- Evidence: official specification says unlock condition trees are evaluated and plants can be placed when conditions are met, but not whether unlock state persists or must re-trigger.
- Resolution: This remains unresolved until explicit simulation evidence is available.

## AMB-006 — Exact semantics when multiple plants spread into one cell

- Status: UNKNOWN
- Conflict: The PDF states that the last plant to spread into a cell wins because neither plant has matured yet. However, special rules, coexistence, and invaded plants may create exceptions.
- Evidence: plant_dataset.json includes special rules like coexist_all_species and spread competition semantics are described in the PDF.
- Resolution: Requires simulator validation and empirical testing.

## AMB-007 — Explicit planting replacement versus spread competition

- Status: RESOLVED
- Evidence: The submission constraints explicitly state that if an action places a plant on an occupied cell, the existing plant is replaced. In contrast, spread competition is described as a different mechanism in the PDF. The two are intentionally distinct.

## AMB-008 — How coexist_all_species affects scoring/counting on one cell

- Status: UNKNOWN
- Conflict: The challenge allows some plants to coexist on a cell, but the final scoring definition counts plants by species on the grid as if cells are occupied by a single plant species.
- Evidence: special rule coexist_all_species exists and the scoring uses species counts and final-state occupancy. The interaction between these is not defined precisely.
- Resolution: Requires simulation validation.

## AMB-009 — How subsurface plants contribute to species counts and scoring

- Status: UNKNOWN
- Conflict: Subsurface growth is explicitly mentioned as an interaction, but the scoring formula counts final species in the grid as though each occupied cell corresponds to a plant species. It is unclear whether subsurface plants count as species presence or only as supporting structure.
- Evidence: Whiteveil Mycelium and related rule sets mention subsurface growth and nutrient transfer networks.
- Resolution: Requires validation against official mechanics.

## AMB-010 — Manual planting on preferred soil when a weakness would immediately invalidate survival

- Status: UNKNOWN
- Conflict: The PDF says plants may only be placed on or spread into preferred soil, but it does not say whether a plant can be deliberately planted there if a weakness would immediately invalidate it.
- Evidence: There are many weakness rules, but no explicit rule says manual placement is prohibited if a cell fails a weakness condition.
- Resolution: Requires empirical validation.

## AMB-011 — Rounding semantics for spread_rate multipliers, maturation multipliers, spread_range multipliers and nutrient modifiers

- Status: UNKNOWN
- Conflict: Several effect objects use numeric multipliers but the PDF does not define how fractional results are rounded or truncated.
- Evidence: animal effects use values like 1.05, 1.1, 1.15 and spread_rate / maturation modifiers may be fractional.
- Resolution: Requires implementation and validation tests.

## AMB-012 — Modifier priority when several conditional modifiers or animals apply

- Status: UNKNOWN
- Conflict: The PDF says multiple modifiers apply in a specific order of priority but does not spell out the exact priority order.
- Evidence: conditional_modifiers and animal effects both apply dynamic changes to plant parameters.
- Resolution: Must be determined empirically or by official simulator behavior.

## AMB-013 — Definition of feature_count for percentage-like values

- Status: BLOCKING
- Conflict: The unlock file uses 0.05 for feature_count(dead_matter), while the text defines feature_count as an absolute count of cells.
- Evidence: PDF says feature_count checks how many cells have a specific world feature; unlocks use decimal values like 0.05 and 20.
- Resolution: Unresolved and must remain flagged because the source is inconsistent.

## AMB-014 — Exact adjacency definition for weakness rules

- Status: UNKNOWN
- Conflict: weakness rules like die_if_neighbors_greater_than and must_be_adjacent_to rely on adjacency, but the challenge text never defines the exact neighbourhood.
- Evidence: row/column/diagonal adjacency is implied but not formally defined.
- Resolution: Requires simulator validation.

## AMB-015 — Exact lifetime accounting for longevity score

- Status: UNKNOWN
- Conflict: The scoring formula defines lifespan but the per-cell and per-plant lifetime accounting in the presence of replacement, spread, and death is not formalized.
- Evidence: Final scoring uses final-state lifespans, but the event sequence before final tick is not specified in the PDF.
- Resolution: Must be validated with empirical runs.

## AMB-016 — Whether events remain logically active/transpired permanently for unlock conditions

- Status: UNKNOWN
- Conflict: The PDF says event_active checks whether a world event has transpired at least once. It does not say whether event state is temporary or permanently stored.
- Evidence: event requirement in plant_unlock_conditions.json uses event conditions such as Drought, Rain, Ash Eclipse.
- Resolution: Unknown until simulator behavior is observed.

## AMB-017 — Whether animals are evaluated before or after plant unlocks each tick

- Status: UNKNOWN
- Conflict: The challenge text describes both animals and unlock evaluation as dynamic world states, but not their relative order.
- Evidence: the PDF semantics imply dynamic update of animals and unlock states, but exact ordering is not given.
- Resolution: Requires empirical validation.

## AMB-018 — Crack generation semantics after earthquakes

- Status: UNKNOWN
- Conflict: The text states cracks form after earthquakes and may alter the world, but it does not define the exact generation pattern.
- Evidence: Earthquake event and crack cells are mentioned; Skyvine can spread over cracks.
- Resolution: Not implementable without empirical level/world data and a reference simulator.

## AMB-019 — Seasonal modifier priority

- Status: LIKELY
- Evidence: conditional_modifiers can include condition names such as season_summer, and the PDF states that if multiple modifiers apply the simulation applies them in a specific order of priority.
- Resolution: This remains unresolved in the data and must be treated as an empirical validation task.

## AMB-020 — Soil and terrain representation consistency

- Status: RESOLVED
- Evidence: The plant dataset and PDF agree that soil IDs are 0,1,2,3 and that water, stone, path, crack and burnt soil are distinct environmental features. The repository does not provide a level layout, so the exact spatial arrangement remains absent.
