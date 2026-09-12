# Scoring and strategy interpretation

The official PDF contains the scoring definitions. The exact hidden coefficients alpha and k are not specified in the challenge data, so any implementation must treat these as unknown calibration parameters rather than guessed constants.

## Formal definitions

- N = total number of species types in the game
- n_i = number of plants of species i present in the final state
- C = total populated cells
- Cmax = N_grid × M_grid
- p_i = n_i / C

Diversity entropy:

H = -Σ p_i log_N(p_i)

where 0 · log_N(0) ≡ 0.

Main score:

H × (C / Cmax)^alpha

Longevity score:

(1 / Cmax) Σ_i Σ_j (lifespan(i,j) / T)^k

Final score:

0.8 × MainScore + 0.2 × LongevityScore

The leaderboard score is a scaled version of this final score with an unknown large multiplier.

## Strategic implications

- Diversity is dominant at 80% of the final score.
- Maximum entropy occurs when represented species are balanced.
- Occupancy also matters through the sample-size factor.
- Empty cells are not free; the effect depends on alpha.
- Species imbalance lowers entropy and can hurt the main score.
- Longevity matters but is secondary.
- Early planting can improve longevity.
- Aggressive spreading species can damage diversity by creating monocultures.
- A final high-coverage but heavily unbalanced garden may score worse than a more balanced one.
- Because alpha and k are hidden, the optimiser must support empirical calibration against official submissions and locally validated simulation outputs.

## Directly supported interpretation

The PDF explicitly says:

- the objective is to create a large and diverse sample;
- avoiding monocultures is important;
- greater plant diversity contributes to a healthier ecosystem;
- the older a plant becomes, the more useful the sample becomes;
- the final scoring uses only the final tick state.

These statements are consistent with the mathematical structure above.
