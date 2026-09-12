from __future__ import annotations

from photospheria.exceptions import ValidationError
from photospheria.submission.models import Submission


def validate_submission(
    submission: Submission,
    strict: bool = False,
    *,
    plant_indices: set[int] | None = None,
    width: int | None = None,
    height: int | None = None,
    total_ticks: int | None = None,
) -> None:
    if submission.version < 1:
        raise ValidationError("Submission version must be at least 1.")
    if submission.serialization_mode not in {"plant_index", "index"}:
        raise ValidationError("Submission serialization_mode must be 'plant_index' or 'index'.")
    if submission.seed is not None and submission.seed < 0:
        raise ValidationError("Seed must be non-negative when provided.")
    for tick_index, tick in enumerate(submission.ticks):
        if total_ticks is not None and tick_index >= total_ticks:
            raise ValidationError(f"Tick {tick_index} is outside the level tick range.")
        if len(tick.actions) > 20:
            raise ValidationError(f"Tick {tick_index} has more than 20 actions.")
        seen: set[tuple[str, int, int]] = set()
        for action in tick.actions:
            if (action.plant, action.x, action.y) in seen:
                raise ValidationError(f"Duplicate planting action on tick {tick_index}: {action}")
            seen.add((action.plant, action.x, action.y))
            if action.x < 0 or action.y < 0:
                raise ValidationError(f"Negative coordinates are invalid in tick {tick_index}: {action}")
            if width is not None and action.x >= width or height is not None and action.y >= height:
                raise ValidationError(f"Action coordinate is outside the level bounds in tick {tick_index}: {action}")
            if isinstance(action.plant, int) and plant_indices is not None and action.plant not in plant_indices:
                raise ValidationError(f"Unknown plant index in tick {tick_index}: {action.plant}")

    if strict:
        # This is intentionally lightweight; the real world model is outside the
        # simulator-foundation phase and should remain isolated from optimiser logic.
        return
