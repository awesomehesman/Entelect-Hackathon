# Classification groups

The provided classifications file defines 15 groups. These are authoritative group names. Any implementation must treat exact wording as case-sensitive and preserve the exact string values in the source data.

## Ground Cover

- Members: Grass, Blue Moss, Razorgrass

## Flowering Plants

- Members: Rose Bush, Lavender, Dwarf Sunflower, Orange Blossom, Moonpetal Lily, Mire Bloom, Ghost Orchid, Sunshard Bloom, Bloodbloom, Phoenix Bloom

## Pollination Plants

- Members: Lavender, Rose Bush, Orange Blossom, Moonpetal Lily, Mire Bloom, Ghost Orchid, Sunshard Bloom

## Seed Plants

- Members: Dwarf Sunflower, Oak Tree, Purple Canopy Tree, Emberroot Tree, Crystal Cactus, Phoenix Bloom, Worldtree Sapling

## Flowering Seed Plants

- Members: Dwarf Sunflower, Phoenix Bloom

## Trees

- Members: Oak Tree, Purple Canopy Tree, Emberroot Tree, Sporewood Tree, Worldtree Sapling

## Bushes / Shrubs

- Members: Rose Bush, Ironthorn Shrub, Living Topiary

## Vines

- Members: Crimson Vine, Skyvine

## Ferns

- Members: Silver Fern, Amber Fern

## Fungi / Mycelial Species

- Members: Glowcap Fungus, Whiteveil Mycelium, Starcap Colony

## Fireadapted Species

- Members: Emberroot Tree, Ashroot Bramble, Phoenix Bloom

## Moisturedependent Species

- Members: Blue Moss, Mire Bloom, Ghost Orchid

## Deep-root Species

- Members: Grass, Silver Fern, Stone Reed, Oak Tree, Emberroot Tree, Crystal Cactus, Amber Fern, Ashroot Bramble, Worldtree Sapling

## Shallowroot Species

- Members: Rose Bush, Lavender, Blue Moss, Crimson Vine, Orange Blossom, Moonpetal Lily, Mire Bloom

## Networkroot Species

- Members: Whiteveil Mycelium, Sporewood Tree, Starcap Colony


## Cross-reference checks

The challenge data includes known exact-string mismatches that must not be silently normalized:

- animals.json uses the requirement target "Shallow-root Species" (with a hyphen)
- classifications.json defines "Shallowroot Species" (without the hyphen)

This difference is considered a specification discrepancy, not a harmless naming variation. The implementation must preserve the exact strings until a higher-authority source resolves it.
