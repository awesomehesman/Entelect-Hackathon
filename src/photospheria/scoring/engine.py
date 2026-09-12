from __future__ import annotations

import math
from collections.abc import Mapping

from photospheria.exceptions import ValidationError


def diversity_entropy(counts: Mapping[str, int], species_total: int = 31) -> float:
    if species_total <= 1:
        raise ValidationError("species_total must be greater than one.")
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return -sum((count / total) * math.log(count / total, species_total) for count in counts.values() if count > 0)


def main_score(entropy: float, occupied_cells: int, maximum_cells: int, *, alpha: float) -> float:
    if maximum_cells <= 0 or occupied_cells < 0 or occupied_cells > maximum_cells:
        raise ValidationError("Occupied and maximum cell counts are invalid.")
    if alpha < 0:
        raise ValidationError("alpha must be non-negative.")
    return entropy * (occupied_cells / maximum_cells) ** alpha


def longevity_score(lifespans: list[float], total_ticks: int, maximum_cells: int, *, k: float) -> float:
    if total_ticks <= 0 or maximum_cells <= 0:
        raise ValidationError("total_ticks and maximum_cells must be positive.")
    if k < 0:
        raise ValidationError("k must be non-negative.")
    return sum((lifespan / total_ticks) ** k for lifespan in lifespans) / maximum_cells


def final_score(main: float, longevity: float) -> float:
    return 0.8 * main + 0.2 * longevity


def main_score_for_config(entropy: float, occupied_cells: int, config: object) -> float:
    alpha = getattr(config, "alpha", None)
    if alpha is None:
        raise ValidationError("LevelConfig does not contain a confirmed alpha value.")
    return main_score(entropy, occupied_cells, int(getattr(config, "maximum_cells")), alpha=float(alpha))


def longevity_score_for_config(lifespans: list[float], config: object) -> float:
    k = getattr(config, "k", None)
    if k is None:
        raise ValidationError("LevelConfig does not contain a confirmed k value.")
    return longevity_score(lifespans, int(getattr(config, "total_ticks")), int(getattr(config, "maximum_cells")), k=float(k))