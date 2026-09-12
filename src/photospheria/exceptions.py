class ValidationError(ValueError):
    """Raised when challenge data or domain objects violate authoritative rules."""


class AmbiguousMechanicError(NotImplementedError):
    """Raised when a mechanic is documented as unresolved and must not be guessed."""

    def __init__(self, amb_id: str, message: str | None = None):
        self.amb_id = amb_id
        self.message = message or f"Unresolved mechanic ({amb_id}) requires explicit evidence before implementation."
        super().__init__(self.message)


class WorldLoadError(ValidationError):
    """Raised when a world/level definition is structurally invalid."""


class ConditionEvaluationError(ValidationError):
    """Raised when a condition cannot be evaluated safely."""
