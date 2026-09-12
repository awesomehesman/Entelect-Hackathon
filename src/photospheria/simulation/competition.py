from __future__ import annotations

from photospheria.exceptions import AmbiguousMechanicError


def resolve_spread_collision(*, existing: object, incoming: object, policy: str = "last_spread_wins") -> object:
    if policy == "last_spread_wins":
        return incoming
    if policy == "invasiveness":
        raise AmbiguousMechanicError("AMB-006", "Invasiveness collision ordering requires official simulator evidence.")
    raise ValueError(f"Unknown competition policy: {policy}")