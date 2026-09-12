from __future__ import annotations

import math


def infer_alpha(main_score: float, entropy: float, density_factor: float) -> float:
    return math.log(main_score / entropy) / math.log(density_factor)