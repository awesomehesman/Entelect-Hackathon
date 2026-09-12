# Data audit

This file records the results of a deterministic audit of the challenge's authoritative JSON files.

## Summary

- Plant entries: 31
- Unlock entries: 26
- Animal entries: 10
- Classification groups: 15
- Initial plantable species: 5
- Plant indices: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
- Index continuity: True
- Duplicate names: none
- Duplicate indices: none

## Plant name and index audit

- All plant names are unique: True
- Plant indices are contiguous from 1 to 31: True
- Initial plants: Grass, Rose Bush, Lavender, Dwarf Sunflower, Oak Tree
- Remaining species with unlock conditions: 26

## Unlock coverage and dependency audit

- Unlock definitions: 26
- Unlock targets covered by plant dataset: True
- Unknown unlock references: none
- Unlock cycles detected: none

## Animal and classification audit

- Animal names: Nectaris, Solwings, Barkskips, Verdelopes, Canorals, Loamcrawlers, Virexids, Grazeleths, Monocryx, Rhizorends
- Unknown animal refs in unlock conditions: none
- Classification groups: Ground Cover, Flowering Plants, Pollination Plants, Seed Plants, Flowering Seed Plants, Trees, Bushes / Shrubs, Vines, Ferns, Fungi / Mycelial Species, Fireadapted Species, Moisturedependent Species, Deep-root Species, Shallowroot Species, Networkroot Species
- Unknown member names in classifications: none
- Exact-string mismatch check: animals.json contains "Shallow-root Species" while classifications.json contains "Shallowroot Species"; this is unresolved and documented in the ambiguity file.

## Rule-type audit

- Condition operators found: ['>', '>=', 'AND', 'OR']
- Weakness types found: ['die_if_isolated', 'die_if_neighbors_greater_than', 'must_be_adjacent_to', 'must_be_burnt_soil', 'no_adjacent_plants', 'no_shade_spread', 'no_shade_survival', 'no_winter_spread', 'shade_required']
- Special rule types found: ['adjacent_maturity_boost', 'adjacent_maturity_penalty', 'adjacent_shade_penalty', 'animal_avoidance', 'auto_unlock_synergy_species', 'boost_whiteveil_spread', 'burnt_soil_maturity_boost', 'burnt_soil_radius', 'coexist_all_species', 'crack_spread', 'dead_matter_only_spread', 'neighbor_spread_slowdown', 'nutrient_transfer_network', 'resurrect_after_destruction', 'shade_radius', 'soil_nutrient_regeneration', 'subsurface_growth']

## Blockers and unresolved findings

- The repository contains no level/world configuration files.
- Exact world layout, events schedule, grid dimensions, soil layout, path/stone/water/cracks and T are absent from the repository.
- The submission format has a field-name discrepancy between "plant_index" and "index".
- The feature_count semantics for decimal values like 0.05 are inconsistent with the PDF wording.
- The exact classification naming mismatch remains unresolved.

## Deterministic note

This audit is generated purely from the authoritative challenge JSON files and does not alter those source files.
