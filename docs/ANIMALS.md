# Animals

The challenge includes 10 animals. Animal presence is dynamic: each animal appears when its requirements are met and disappears when those requirements are no longer satisfied. This is a core simulation rule from the PDF and must be respected.

The animals are:

- Nectaris
- Solwings
- Barkskips
- Verdelopes
- Canorals
- Loamcrawlers
- Virexids
- Grazeleths
- Monocryx
- Rhizorends

## Detailed records

## Nectaris (nectaris)

- Appearance requirements: {"type": "OR", "conditions": [{"type": "coverage", "species": ["Lavender"], "threshold": 0.02, "operator": ">="}, {"type": "group_coverage", "species_group": ["Lavender", "Rose Bush", "Dwarf Sunflower", "Orange Blossom"], "threshold": 0.02, "operator": ">="}]}
- Effects: [{"type": "spread_rate", "target": "Pollination Plants", "value": 1.5, "mode": "multiply"}, {"type": "maturation_rate", "target": "Flowering Plants", "value": 1.1, "mode": "multiply"}]

## Solwings (solwings)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "coverage", "species": ["Dwarf Sunflower"], "threshold": 0.03, "operator": ">="}, {"type": "coverage", "species": ["Rose Bush"], "threshold": 0.02, "operator": ">="}]}
- Effects: [{"type": "seed_dispersal", "target": "Flowering Seed Plants", "value": 1.5, "mode": "multiply"}]

## Barkskips (barkskips)

- Appearance requirements: {"type": "OR", "conditions": [{"type": "count", "species": "Oak Tree", "threshold": 8, "operator": ">="}, {"type": "count", "species": "Worldtree Sapling", "threshold": 1, "operator": ">="}]}
- Effects: [{"type": "spread_rate", "target": "Trees", "value": 1.1, "mode": "multiply"}]

## Verdelopes (verdelopes)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "coverage", "species": ["Grass"], "threshold": 0.05, "operator": ">="}]}
- Effects: [{"type": "spread_rate", "target": "Grass", "value": 1.1, "mode": "multiply"}, {"type": "maturation_rate", "target": "Rose Bush", "value": 0.9, "mode": "multiply"}]

## Canorals (canorals)

- Appearance requirements: {"type": "OR", "conditions": [{"type": "count", "species_group": ["Trees"], "threshold": 10, "operator": ">="}, {"type": "group_coverage", "species_group": ["Flowering Plants"], "threshold": 0.05, "operator": ">="}, {"type": "count", "species": "Worldtree Sapling", "threshold": 1, "operator": ">="}]}
- Effects: [{"type": "spread_range", "target": "Seed Plants", "value": 1.05, "mode": "multiply"}]

## Loamcrawlers (loamcrawlers)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "coverage", "species": ["Grass"], "threshold": 0.04, "operator": ">="}, {"type": "count", "species": "Rose Bush", "threshold": 10, "operator": ">="}]}
- Effects: [{"type": "soil_nutrient_regeneration", "target": "soil", "value": 1.05, "mode": "multiply"}]

## Virexids (virexids)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "count", "species": "Lavender", "threshold": 10, "operator": ">="}, {"type": "count", "species": "Grass", "threshold": 10, "operator": ">="}]}
- Effects: [{"type": "spread_rate", "target": "Shallow-root Species", "value": 1.1, "mode": "multiply"}]

## Grazeleths (grazeleths)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "coverage", "species": ["Grass"], "threshold": 0.04, "operator": ">="}, {"type": "count", "species_group": ["Rose Bush", "Lavender", "Orange Blossom"], "threshold": 10, "operator": ">="}]}
- Effects: [{"type": "soil_nutrient_regeneration", "target": "soil", "value": 1.15, "mode": "multiply"}, {"type": "regression_rate", "target": "Flowering Plants", "value": 2, "mode": "multiply"}]

## Monocryx (monocryx)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "dominance", "mode": "single_species", "threshold": 0.5}]}
- Effects: []

## Rhizorends (rhizorends)

- Appearance requirements: {"type": "AND", "conditions": [{"type": "count", "species_group": ["Shallow-root Species"], "threshold": 25, "operator": ">="}]}
- Effects: []


## Animal notes

The animals are not decorative; they affect plant growth, spread rate, maturation, seed dispersal, and even nutrient regeneration. Unlock conditions also sometimes depend on the presence or absence of fauna. Several animals gate plant unlocks directly.
