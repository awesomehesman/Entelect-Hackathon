# Implementation status

## Phase 1: simulator foundation

Status: foundation contracts implemented; full Phase 1 acceptance is not yet approved.

### Scope covered

- Authoritative challenge data ingestion from the official resource files.
- Safe condition evaluation with strict ambiguity handling.
- Strict data validation for plant, unlock, animal, and classification integrity.
- Level-definition validation for the world model contract.
- Submission schema validation and CLI guardrails.
- Documentation of unresolved mechanics and the explicit no-guessing policy.
- Pure scoring, spread-geometry, and safe-mechanics helpers with focused tests.

### Explicitly out of scope

- Final optimiser logic.
- Competitive submission generation.
- Tick engine implementation.
- Any simulation behaviour that depends on undocumented or unresolved world mechanics.
- Full animal effect application and dynamic world-state evaluation.
- Full scoring integration with final world state.

### Ambiguity guardrails in force

- `feature_count` conditions raise `AmbiguousMechanicError` instead of guessing.
- Required unresolved mechanics `AMB-004`, `AMB-006`, `AMB-008`, `AMB-009`, `AMB-011`, `AMB-012`, `AMB-014`, and `AMB-018` have explicit guard interfaces.
- Unsupported or unsafe condition leaves raise `ConditionEvaluationError`.
- The exact string mismatch between `Shallow-root Species` and `Shallowroot Species` is preserved as a documented discrepancy rather than being silently normalized.

### Validation

The project remains in the deterministic foundation phase and is validated through unit and integration tests only, without any competition-optimiser logic. A full tick engine and official-world validation are still blockers for claiming complete simulator readiness.
