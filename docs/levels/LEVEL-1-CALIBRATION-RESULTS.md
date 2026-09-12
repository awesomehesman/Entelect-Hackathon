# Level 1 Calibration 01 official results

Calibration 01 was evaluated successfully by the official Level 1 evaluator.

## Observed configuration

- World: `50 x 50`
- Ticks: `500`
- Seasons: enabled
- Season transitions: Summer at tick `100`, Autumn at `200`, Winter at `300`, Spring at `400`
- Animals: disabled
- Weather: disabled
- Accepted action key: `plant_index`
- Accepted action tick: `499`
- Accepted coordinates: `(25,25)`, `(25,26)`, `(26,25)`, `(26,26)`, `(24,25)`
- Accepted species: Grass, Rose Bush, Lavender, Dwarf Sunflower, Oak Tree
- `N = 31`
- `Cmax = 2500`
- Evaluator leaderboard scale: approximately `1e9`

The five observed coordinates do not establish that every coordinate is plantable or that every cell is soil.

## Official statistics

```text
score = 0.000750686504099727
leaderboard_score = 750687
main_score = 0.0009373581301246587
longevity_score = 0.000004
entropy = 0.4686790650623293
total_plants_planted_C = 5
unlocked_plant_types = 5
density_factor = 0.002
N = 31
Cmax = 2500
```

Plant counts were one each for Grass, Rose Bush, Dwarf Sunflower, Lavender, and Oak Tree; every other species had count zero.

## Alpha inference

Using:

`main_score = entropy * density_factor ** alpha`

the official values produce:

```text
alpha = 1.0
```

This is empirically inferred from the official evaluator output and is observed for this Level 1 calibration result. It is not a fabricated default for hidden levels.

## K investigation

With five plants placed at tick 499, `longevity_score = 0.000004` is consistent with `k = 1` if each final plant receives one scored lifespan tick:

`5 * (1 / 500) / 2500 = 0.000004`

The single observation does not uniquely determine `k` or the exact lifespan boundary convention. `k = 1` is therefore empirically suspected, not promoted to a confirmed constant. A second observation with a different planting tick and known survival would be needed to uniquely identify both `k` and the lifespan convention.
