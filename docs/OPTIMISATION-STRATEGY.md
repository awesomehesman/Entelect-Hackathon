# Optimisation strategy (future work)

This section documents the architecture to be used later, but it is not an implementation plan. The optimiser must not be treated as a simple "unlock everything" script.

The final objective is to optimise the final state under:

- diversity entropy
- total occupied cells
- uniformity among species
- longevity
- unlock timing
- spreading behaviour
- competition
- animals
- terrain
- events
- seasons
- 20 manual actions per tick
- finite T

## Future phases

- Phase A — deterministic simulator
- Phase B — exact scoring surrogate
- Phase C — valid baseline planner
- Phase D — unlock planner
- Phase E — spatial planner
- Phase F — diversity balancing
- Phase G — lifespan optimisation
- Phase H — search / metaheuristics
- Phase I — hidden-parameter calibration
- Phase J — leaderboard candidate generation

## Candidate techniques

- dependency scheduling
- event-aware planning
- greedy constructive search
- beam search
- hill climbing
- simulated annealing
- evolutionary strategies
- Monte Carlo search
- local search
- mutation of action schedules
- spatial tiling / zoning
- final-state repair
- diversity balancing

## Important constraint

The official scoring formula depends on final-state diversity and occupancy, but alpha and k are hidden. The optimiser must therefore support empirical calibration using official submissions and internal validation runs rather than assuming constants.
