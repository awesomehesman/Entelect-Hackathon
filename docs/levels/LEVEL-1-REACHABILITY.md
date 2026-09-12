# Level 1 reachability

This table uses only the accepted Level 1 facts: animals are disabled, weather conditions are disabled, seasons exist, and the five initial species are available. It does not assume a season schedule, terrain layout, soil distribution, or hidden simulator behavior.

Reachability is computed by `photospheria.levels.level1.analyze_level1_reachability` from the authoritative plant, unlock, and animal JSON files.

| Species            | Class                     | Reason                                                                        |
| ------------------ | ------------------------- | ----------------------------------------------------------------------------- |
| Grass              | A. DEFINITELY REACHABLE   | Initial species                                                               |
| Rose Bush          | A. DEFINITELY REACHABLE   | Initial species                                                               |
| Lavender           | A. DEFINITELY REACHABLE   | Initial species                                                               |
| Dwarf Sunflower    | A. DEFINITELY REACHABLE   | Initial species                                                               |
| Oak Tree           | A. DEFINITELY REACHABLE   | Initial species                                                               |
| Blue Moss          | B. DEFINITELY UNREACHABLE | Requires disabled Loamcrawlers                                                |
| Orange Blossom     | B. DEFINITELY UNREACHABLE | Requires disabled Nectaris or Solwings                                        |
| Glowcap Fungus     | B. DEFINITELY UNREACHABLE | Requires disabled Loamcrawlers                                                |
| Stone Reed         | B. DEFINITELY UNREACHABLE | Requires disabled Virexids                                                    |
| Crimson Vine       | B. DEFINITELY UNREACHABLE | Requires disabled Nectaris or Canorals                                        |
| Silver Fern        | B. DEFINITELY UNREACHABLE | Requires disabled Loamcrawlers or Grazeleths                                  |
| Purple Canopy Tree | B. DEFINITELY UNREACHABLE | Requires unavailable Blue Moss and Crimson Vine                               |
| Whiteveil Mycelium | B. DEFINITELY UNREACHABLE | Requires unavailable Glowcap Fungus and an unavailable animal branch          |
| Emberroot Tree     | B. DEFINITELY UNREACHABLE | Requires unavailable Whiteveil Mycelium                                       |
| Moonpetal Lily     | B. DEFINITELY UNREACHABLE | Requires disabled Nectaris                                                    |
| Ironthorn Shrub    | B. DEFINITELY UNREACHABLE | Requires disabled Grazeleths                                                  |
| Crystal Cactus     | B. DEFINITELY UNREACHABLE | Requires disabled Drought event                                               |
| Mire Bloom         | B. DEFINITELY UNREACHABLE | Requires disabled Rain event                                                  |
| Razorgrass         | B. DEFINITELY UNREACHABLE | Requires disabled Verdelopes                                                  |
| Skyvine            | B. DEFINITELY UNREACHABLE | Requires unavailable Crimson Vine and Purple Canopy Tree                      |
| Ghost Orchid       | B. DEFINITELY UNREACHABLE | Requires unavailable Glowcap Fungus and Moonpetal Lily                        |
| Amber Fern         | B. DEFINITELY UNREACHABLE | Requires unavailable Silver Fern and disabled Loamcrawlers                    |
| Thornheart Bramble | B. DEFINITELY UNREACHABLE | Requires unavailable Ironthorn Shrub and Crimson Vine                         |
| Sporewood Tree     | B. DEFINITELY UNREACHABLE | Requires unavailable Whiteveil Mycelium and Purple Canopy Tree                |
| Sunshard Bloom     | B. DEFINITELY UNREACHABLE | Requires unavailable Orange Blossom/Moonpetal Lily and disabled animals       |
| Ashroot Bramble    | B. DEFINITELY UNREACHABLE | Requires unavailable Emberroot Tree; feature count is also unresolved         |
| Living Topiary     | B. DEFINITELY UNREACHABLE | Requires unavailable Silver Fern/Purple Canopy Tree and disabled Canorals     |
| Bloodbloom         | B. DEFINITELY UNREACHABLE | Requires unavailable Crimson Vine and disabled Rhizorends                     |
| Starcap Colony     | B. DEFINITELY UNREACHABLE | Requires unavailable Whiteveil Mycelium, Glowcap Fungus, and Ghost Orchid     |
| Phoenix Bloom      | B. DEFINITELY UNREACHABLE | Requires disabled Ash Eclipse event                                           |
| Worldtree Sapling  | B. DEFINITELY UNREACHABLE | Requires unavailable Purple Canopy Tree/Sporewood Tree and disabled Barkskips |

## Totals

- Definitely reachable: **5**
- Definitely unreachable: **26**
- Conditional/unknown: **0** under the accepted Level 1 constraints

The absence of conditional entries does not resolve terrain, seasons, feature-count semantics, or spread behavior. It only means those unknowns cannot make any currently locked species reachable because every locked path is already blocked by a disabled event, disabled animal, or an unavailable dependency.
