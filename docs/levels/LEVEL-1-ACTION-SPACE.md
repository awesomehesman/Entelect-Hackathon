# Level 1 action-space model

The `Level1Constraints` object in `src/photospheria/levels/level1.py` records the accepted Level 1 action bounds without encoding any unknown terrain or soil layout.

- Tick range: `0..499`
- Row range: `0..49`
- Column range: `0..49`
- Maximum explicit actions per tick: `20`
- Initial species: Grass, Rose Bush, Lavender, Dwarf Sunflower, Oak Tree
- Explicit replacement: allowed by the official PDF
- Unlock rule: only currently unlocked species may be explicitly planted

These constraints establish coordinate and schedule shape only. They do not establish that every coordinate is soil or that a placement will survive.
