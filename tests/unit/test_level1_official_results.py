from __future__ import annotations

import math

import pytest

from photospheria.levels.level1 import Level1Constraints
from photospheria.scoring import diversity_entropy, infer_alpha


def test_official_calibration_alpha_is_one() -> None:
    alpha = infer_alpha(0.0009373581301246587, 0.4686790650623293, 0.002)
    assert alpha == pytest.approx(1.0)


def test_official_calibration_longevity_is_consistent_with_k_one() -> None:
    assert (5 * (1 / 500)) / 2500 == pytest.approx(0.000004)
    assert not math.isclose((5 * (1 / 500) ** 2) / 2500, 0.000004)


@pytest.mark.parametrize(
    ("tick", "season"),
    [(0, "Spring"), (99, "Spring"), (100, "Summer"), (199, "Summer"), (200, "Autumn"), (299, "Autumn"), (300, "Winter"), (399, "Winter"), (400, "Spring"), (499, "Spring")],
)
def test_official_level1_season_boundaries(tick: int, season: str) -> None:
    assert Level1Constraints.season_at(tick) == season


def test_balanced_five_species_entropy_and_alpha_one_main_score() -> None:
    entropy = diversity_entropy({"Grass": 500, "Rose Bush": 500, "Lavender": 500, "Dwarf Sunflower": 500, "Oak Tree": 500}, 31)
    assert entropy == pytest.approx(math.log(5, 31))
    assert entropy * (2500 / 2500) == pytest.approx(entropy)