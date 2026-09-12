from __future__ import annotations

from collections.abc import Iterable


def events_at(schedule: Iterable[dict[str, object]], tick: int) -> tuple[dict[str, object], ...]:
    return tuple(event for event in schedule if int(event["tick"]) == tick)