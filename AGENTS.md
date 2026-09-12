# AGENTS.md

# Mission

Build a deterministic optimiser for the Entelect Hack<IT> "Root Cause Analysis" challenge whose goal is to maximise leaderboard score.

# Priority

Correct simulation semantics first.
Valid submission second.
Optimisation third.
Runtime optimisation fourth.

A high-scoring result produced by an inaccurate simulator is unacceptable.

# Authoritative sources

Order of authority:

1. official problem statement
2. supplied challenge JSON datasets
3. supplied level/world files
4. empirically verified observations from official submissions
5. repository documentation
6. implementation assumptions

Never overwrite a higher-authority source using a lower-authority assumption.

# Non-negotiable rules

- Never fabricate undocumented game mechanics.
- Never silently resolve specification contradictions.
- Never modify official challenge resources.
- Never manually craft the final solution independently of the solver.
- Every submitted solution must be reproducible from source.
- Solver execution must be deterministic for a fixed seed/configuration.
- Preserve previous best-known valid solutions.
- Never replace a higher-scoring known-valid solution unless the replacement is demonstrably superior.
- Separate simulation correctness from optimisation logic.
- Separate challenge data ingestion from simulation.
- Separate simulation from scoring.
- Separate search/optimisation from submission serialization.
- Validate every action before producing the final JSON.
- Maximum twenty explicit planting actions per tick.
- Do not plant unavailable/locked species.
- Do not assume an unlock persists unless the official simulation semantics imply that.
- Only the final world state contributes to scoring.
- Plants dead before final scoring contribute nothing.
- Keep experimental optimisation strategies isolated.
- Record benchmark scores and solver configuration for every serious candidate.

# Working workflow

For every implementation phase:

Understand
→ Document
→ Implement
→ Unit test
→ Simulation test
→ Validate
→ Benchmark
→ Compare with current best
→ Only then promote.

# Competition workflow

Never repeatedly submit random changes to the official leaderboard.

Prefer:

1. reproduce mechanics locally
2. validate candidate locally
3. compare candidate against current local best
4. submit only materially improved candidates

# Git discipline

Use small conventional commits.
Do not mix documentation, simulator, optimisation and generated submission changes unnecessarily.
