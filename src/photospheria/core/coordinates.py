from __future__ import annotations

from photospheria.exceptions import ValidationError


def validate_coordinate(row: int, col: int, rows: int, columns: int) -> None:
    if not 0 <= row < rows or not 0 <= col < columns:
        raise ValidationError(f"Coordinates must be in rows 0..{rows - 1} and cols 0..{columns - 1}.")