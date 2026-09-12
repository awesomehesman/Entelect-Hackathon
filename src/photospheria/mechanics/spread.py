from __future__ import annotations

from collections.abc import Iterator

from photospheria.exceptions import ValidationError


def spread_offsets(spread_type: str, spread_range: int) -> tuple[tuple[int, int], ...]:
    if spread_range < 1:
        raise ValidationError("spread_range must be positive.")
    offsets: set[tuple[int, int]] = set()
    for dx in range(-spread_range, spread_range + 1):
        for dy in range(-spread_range, spread_range + 1):
            if (dx, dy) == (0, 0):
                continue
            distance = max(abs(dx), abs(dy))
            name = spread_type.lower()
            if name == "vonneumann" and abs(dx) + abs(dy) <= spread_range:
                offsets.add((dx, dy))
            elif name == "moore" and distance <= spread_range:
                offsets.add((dx, dy))
            elif name == "row" and dy == 0 and abs(dx) <= spread_range:
                offsets.add((dx, dy))
            elif name == "column" and dx == 0 and abs(dy) <= spread_range:
                offsets.add((dx, dy))
            elif name == "crosshatch" and abs(dx) == abs(dy) and distance <= spread_range:
                offsets.add((dx, dy))
    if not offsets:
        raise ValidationError(f"Unsupported spread type: {spread_type!r}")
    return tuple(sorted(offsets))


def spread_targets(x: int, y: int, width: int, height: int, spread_type: str, spread_range: int) -> Iterator[tuple[int, int]]:
    if width <= 0 or height <= 0:
        raise ValidationError("World dimensions must be positive.")
    for dx, dy in spread_offsets(spread_type, spread_range):
        target_x, target_y = x + dx, y + dy
        if 0 <= target_x < width and 0 <= target_y < height:
            yield target_x, target_y