from __future__ import annotations

import pytest

from photospheria.mechanics.spread import spread_targets
from photospheria.scoring import diversity_entropy, final_score


def test_entropy_has_expected_distribution_properties() -> None:
    assert diversity_entropy({"Grass": 10}) == pytest.approx(0.0)
    assert diversity_entropy({"Grass": 5, "Rose Bush": 5}) > diversity_entropy({"Grass": 9, "Rose Bush": 1})
    assert diversity_entropy({str(index): 1 for index in range(31)}) == pytest.approx(1.0)


def test_final_score_uses_documented_weights() -> None:
    assert final_score(0.75, 0.25) == pytest.approx(0.65)


def test_spread_geometry_clips_edges_and_honours_range() -> None:
    assert set(spread_targets(0, 0, 5, 5, "VonNeumann", 1)) == {(1, 0), (0, 1)}
    assert len(set(spread_targets(2, 2, 7, 7, "Moore", 2))) == 24
    assert set(spread_targets(2, 2, 7, 7, "Row", 2)) == {(0, 2), (1, 2), (3, 2), (4, 2)}
    assert set(spread_targets(2, 2, 7, 7, "Column", 2)) == {(2, 0), (2, 1), (2, 3), (2, 4)}
    assert set(spread_targets(2, 2, 7, 7, "CrossHatch", 2)) == {(0, 0), (1, 1), (3, 1), (4, 0), (0, 4), (1, 3), (3, 3), (4, 4)}