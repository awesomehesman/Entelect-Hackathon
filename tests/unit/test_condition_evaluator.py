from __future__ import annotations

import pytest

from photospheria.conditions.evaluator import evaluate_condition
from photospheria.exceptions import AmbiguousMechanicError


def test_unlock_style_logic_works_for_authoritative_shapes() -> None:
    ctx = {
        "species_count": {"Grass": 3},
        "events": {"Rain": True},
        "species_present": {"Loamcrawlers": True},
    }

    assert evaluate_condition({"op": "AND", "children": [{"type": "count", "species": "Grass", "threshold": 1, "operator": ">="}, {"type": "event", "event": "Rain"}]}, ctx) is True
    assert evaluate_condition({"type": "OR", "conditions": [{"type": "species_present", "species": "Loamcrawlers"}, {"type": "event", "event": "Drought"}]}, ctx) is True


def test_group_coverage_and_species_absence_are_supported() -> None:
    ctx = {
        "coverage": {"Grass": 0.10, "Rose Bush": 0.05},
        "species_present": {"Monocryx": False},
        "species_count": {"Rose Bush": 6, "Lavender": 4},
    }

    assert evaluate_condition({"type": "group_coverage", "species_group": ["Grass", "Rose Bush"], "threshold": 0.08, "operator": ">="}, ctx) is True
    assert evaluate_condition({"type": "species_absent", "species": "Monocryx"}, ctx) is True


def test_ambiguous_feature_count_remains_blocked() -> None:
    with pytest.raises(AmbiguousMechanicError):
        evaluate_condition({"type": "feature_count", "feature": "dead_matter", "operator": ">", "value": 0.05}, {"coverage": {"dead_matter": 0.10}})