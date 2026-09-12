# Plant catalogue

The plant dataset contains 31 species total. The five initially plantable species are: Grass, Rose Bush, Lavender, Dwarf Sunflower, and Oak Tree. The remaining 26 species are unlock-gated.

## Full species table

| Plant | Index | Initial availability | Maturity time | Spread rate | Spread mechanism | Spread type | Spread range | Root type | Invasiveness rank | Preferred soil | Weaknesses | Special rules | Role | Unlock dependency |
| --- | ---: | --- | ---: | ---: | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| Grass | 1 | Yes | 1 | 2 | Shoots | VonNeumann | 1 | Deep | 1 | [0, 1] | [{'type': 'no_shade_survival'}] | [] | Fast filler plant | — |
| Rose Bush | 2 | Yes | 10 | 2 | Shoots | Row | 1 | Shallow | 2 | [0, 1] | [{'type': 'no_winter_spread'}] | [] | Slow directional spreader | — |
| Blue Moss | 3 | Locked | 3 | 3 | Spores | Moore | 1 | Shallow | 3 | [0, 1] | [{'type': 'die_if_neighbors_greater_than', 'value': 4}] | [{'type': 'adjacent_maturity_boost', 'value': 1}] | Support / synergy plant | Blue Moss |
| Crimson Vine | 4 | Locked | 4 | 1 | Shoots | Column | 1 | Shallow | 9 | [0, 1] | [{'type': 'die_if_isolated'}] | [] | Needy creeper | Crimson Vine |
| Dwarf Sunflower | 5 | Yes | 5 | 4 | Seeds | CrossHatch | 2 | Shallow | 4 | [0, 1] | [{'type': 'no_shade_spread'}] | [{'type': 'adjacent_shade_penalty'}] | Spacing challenge | — |
| Lavender | 6 | Yes | 4 | 3 | Pollination | CrossHatch | 1 | Shallow | 2 | [0, 1] | [{'type': 'no_winter_spread'}] | [] | Pollination engine | — |
| Orange Blossom | 7 | Locked | 6 | 3 | Shoots | VonNeumann | 4 | Shallow | 7 | [0, 1] | [] | [] | Summer burst expander | Orange Blossom |
| Silver Fern | 8 | Locked | 7 | 4 | Shoots | Row | 1 | Deep | 6 | [0, 1] | [] | [] | Tank / anchor | Silver Fern |
| Glowcap Fungus | 9 | Locked | 2 | 3 | Spores | VonNeumann | 1 | None | 8 | [0, 1] | [] | [{'type': 'adjacent_maturity_penalty', 'value': 2}, {'type': 'dead_matter_only_spread'}] | Decay mechanic | Glowcap Fungus |
| Purple Canopy Tree | 10 | Locked | 15 | 6 | Seeds | Moore | 1 | Deep | 10 | [0, 1] | [] | [{'type': 'shade_radius', 'value': 2}] | Shade caster | Purple Canopy Tree |
| Stone Reed | 11 | Locked | 5 | 4 | Shoots | Column | 1 | Shallow | 5 | [0, 1] | [{'type': 'must_be_adjacent_to', 'feature': 'rock_or_path'}] | [] | Terrain exploitation | Stone Reed |
| Oak Tree | 12 | Yes | 20 | 7 | Seeds | Moore | 2 | Deep | 10 | [0, 1] | [] | [{'type': 'shade_radius', 'value': 4}] | Late-game dominant | — |
| Emberroot Tree | 13 | Locked | 15 | 6 | Seeds | Moore | 4 | Deep | 13 | [0, 1] | [] | [{'type': 'burnt_soil_radius', 'value': 2}] | Hazard species | Emberroot Tree |
| Whiteveil Mycelium | 14 | Locked | 8 | 2 | Shoots | CrossHatch | 2 | Deep | 11 | [0, 1] | [] | [{'type': 'subsurface_growth'}, {'type': 'nutrient_transfer_network'}] | System-level synergy | Whiteveil Mycelium |
| Moonpetal Lily | 15 | Locked | 5 | 4 | Pollination | Column | 2 | Shallow | 4 | [0, 1] | [{'type': 'shade_required'}] | [] | Shade specialist | Moonpetal Lily |
| Ironthorn Shrub | 16 | Locked | 7 | 4 | Shoots | VonNeumann | 1 | Deep | 6 | [0, 1] | [] | [] | Defensive protector | Ironthorn Shrub |
| Crystal Cactus | 17 | Locked | 8 | 4 | Seeds | VonNeumann | 2 | Deep | 5 | [0, 1] | [] | [{'type': 'soil_nutrient_regeneration'}] | Soil restoration | Crystal Cactus |
| Mire Bloom | 18 | Locked | 5 | 3 | Pollination | VonNeumann | 1 | Shallow | 7 | [0, 1, 2] | [{'type': 'must_be_adjacent_to', 'feature': 'water'}] | [] | Moisture dependent | Mire Bloom |
| Razorgrass | 19 | Locked | 2 | 1 | Shoots | CrossHatch | 1 | Deep | 8 | [0, 1] | [] | [{'type': 'animal_avoidance', 'species': 'Verdelopes'}] | Deterrent | Razorgrass |
| Skyvine | 20 | Locked | 4 | 1 | Shoots | Column | 1 | Shallow | 12 | [0, 1] | [] | [{'type': 'crack_spread'}] | Terrain bypass | Skyvine |
| Ghost Orchid | 21 | Locked | 8 | 4 | Pollination | Moore | 1 | Deep | 11 | [0, 1] | [{'type': 'shade_required'}] | [] | Rare shade species | Ghost Orchid |
| Amber Fern | 22 | Locked | 12 | 6 | Spores | VonNeumann | 1 | Deep | 10 | [0, 1] | [] | [] | Stability species | Amber Fern |
| Thornheart Bramble | 23 | Locked | 6 | 3 | Shoots | VonNeumann | 3 | Shallow | 9 | [0, 1] | [] | [{'type': 'neighbor_spread_slowdown', 'value': 1}] | Territory control | Thornheart Bramble |
| Sporewood Tree | 24 | Locked | 15 | 4 | Spores | Moore | 1 | Shallow | 12 | [0, 1] | [] | [{'type': 'boost_whiteveil_spread', 'value': 1}] | Fungal ecosystem builder | Sporewood Tree |
| Sunshard Bloom | 25 | Locked | 10 | 4 | Pollination | Moore | 1 | Shallow | 15 | [0, 1] | [] | [{'type': 'adjacent_maturity_boost', 'value': 2}] | Ultimate support | Sunshard Bloom |
| Ashroot Bramble | 26 | Locked | 5 | 3 | Shoots | VonNeumann | 2 | Deep | 13 | [3] | [{'type': 'must_be_burnt_soil'}] | [] | Fire specialist | Ashroot Bramble |
| Living Topiary | 27 | Locked | 12 | 4 | Shoots | CrossHatch | 2 | Deep | 14 | [0, 1] | [{'type': 'no_adjacent_plants'}] | [] | Adaptive exclusion species | Living Topiary |
| Bloodbloom | 28 | Locked | 6 | 4 | Pollination | Moore | 3 | Shallow | 14 | [0, 1] | [] | [{'type': 'adjacent_maturity_penalty', 'value': 2}] | Ecosystem predator | Bloodbloom |
| Starcap Colony | 29 | Locked | 10 | 2 | Spores | CrossHatch | 2 | Deep | 16 | [0, 1] | [] | [{'type': 'coexist_all_species'}] | Diversity anchor | Starcap Colony |
| Phoenix Bloom | 30 | Locked | 7 | 3 | Seeds | Moore | 3 | Deep | 17 | [0, 1] | [] | [{'type': 'resurrect_after_destruction'}, {'type': 'burnt_soil_maturity_boost', 'value': 2}] | Regeneration specialist | Phoenix Bloom |
| Worldtree Sapling | 31 | Locked | 25 | 10 | Seeds | Moore | 2 | Deep | 18 | [0, 1] | [] | [{'type': 'auto_unlock_synergy_species', 'species': ['Barkskips', 'Canorals']}] | Final ecosystem goal | Worldtree Sapling |

## Especially important species

These species are strategically important because their rules have outsized ecosystem effects or unlock chains.

- Crimson Vine: shallow-root vine, spread type Column, rule die_if_isolated, unlock is tied to Nectaris/Canorals and Rose Bush/Lavender coverage. It is a heavy dependency in several unlock chains.
- Purple Canopy Tree: one of the major late-game shade and coverage anchors; requirement chains include Blue Moss and Crimson Vine coverage. It is an unlock prerequisite for Skyvine, Sporewood Tree, Emberroot Tree and Worldtree Sapling.
- Oak Tree: one of the initial five, with large shade radius and high maturity time; it is a central forest anchor and a trigger for Barkskips and the Worldtree chain.
- Emberroot Tree: hazard species with burnt_soil_radius and unlock dependencies; it triggers Ashroot Bramble and Phoenix Bloom.
- Whiteveil Mycelium: subsurface growth and nutrient transfer network; central to mycelial ecosystems and unlock prerequisites.
- Razorgrass: deterrent species with animal_avoidance against Verdelopes; tied to Grass coverage and animal-specific strategy.
- Skyvine: crack-spread species with low spread rate but a strong terrain exploit; unlock depends on Crimson Vine and Purple Canopy Tree.
- Starcap Colony: coexist_all_species species; central to fungal group and requires Whiteveil Mycelium, Glowcap Fungus and Ghost Orchid coverage.
- Phoenix Bloom: regeneration specialist with resurrect_after_destruction and burnt_soil_maturity_boost; only unlocks under Ash Eclipse and after Emberroot/Ashroot conditions.
- Worldtree Sapling: final ecosystem goal; unlock requires Oak Tree, Purple Canopy Tree, Sporewood Tree, and Barkskips.

## Strategic notes

The data does not provide a prescriptive ranking of species. Instead, the plant entries establish actual deployment rules, spread geometry, soil preference, and weakness/special behaviour. These are the correct basis for later strategy design.
