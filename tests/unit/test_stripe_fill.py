"""Tests for the vertical-stripe fill planner."""

from __future__ import annotations

from photospheria.data.loaders import load_challenge_data
from photospheria.levels.configs import level_config
from photospheria.solver.stripe_fill import plan_stripe_fill

STARTERS = ["Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree"]


def _species():
    plants = {p.plant: p for p in load_challenge_data()["plants"]}
    return [plants[n] for n in STARTERS]


def test_plan_has_balanced_distribution_and_in_window():
    config = level_config(1)
    plan = plan_stripe_fill(config, _species())
    # every action is inside the survival window
    start, end = plan.survival_window
    for tick, actions in plan.actions_by_tick.items():
        assert start <= tick <= end
        assert len(actions) <= config.max_actions_per_tick
    # Check we have all 5 species
    counts: dict[int, int] = {}
    for actions in plan.actions_by_tick.values():
        for idx, _r, _c in actions:
            counts[idx] = counts.get(idx, 0) + 1
    assert len(counts) == 5
    # Roughly balanced (within 10%)
    values = list(counts.values())
    assert max(values) - min(values) <= max(values) * 0.1


def test_all_cells_distinct():
    config = level_config(2)
    plan = plan_stripe_fill(config, _species())
    cells = [(r, c) for actions in plan.actions_by_tick.values() for _i, r, c in actions]
    assert len(cells) == len(set(cells))
