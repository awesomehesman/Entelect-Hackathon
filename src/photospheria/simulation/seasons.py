from __future__ import annotations

from collections.abc import Iterable

from photospheria.exceptions import ValidationError


def season_at(schedule: Iterable[tuple[int, str]], tick: int, total_ticks: int) -> str:
    if not 0 <= tick < total_ticks:
        raise ValidationError(f"Tick must be in 0..{total_ticks - 1}: {tick}")
    entries = tuple(schedule)
    return max((entry for entry in entries if entry[0] <= tick), key=lambda entry: entry[0])[1]