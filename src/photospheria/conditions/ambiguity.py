from __future__ import annotations

from photospheria.exceptions import AmbiguousMechanicError


def require_resolved_mechanic(amb_id: str) -> None:
    unresolved = {"AMB-004", "AMB-006", "AMB-008", "AMB-009", "AMB-011", "AMB-012", "AMB-014", "AMB-018"}
    if amb_id in unresolved:
        raise AmbiguousMechanicError(amb_id)