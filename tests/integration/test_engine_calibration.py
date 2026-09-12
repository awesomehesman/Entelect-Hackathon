"""Regression guard: the full engine must reproduce the official Level 1 log.

The official Level 1 evaluation (SubmissionLogs/dfec4b87-...-evaluation.log)
reported exact statistics for a 5-plant, tick-499 submission. The calibrated
engine must reproduce every reported field to float precision. If this test
fails, the simulator's scoring/lifespan/nutrient model has drifted from the
official evaluator and must not be trusted for candidate promotion.
"""

from __future__ import annotations

from photospheria.data.loaders import load_challenge_data
from photospheria.simulation.full_engine import Simulator, WorldConfig

LEVEL1_SEASONS = ((0, "Spring"), (100, "Summer"), (200, "Autumn"), (300, "Winter"), (400, "Spring"))


def _run_official_level1():
    data = load_challenge_data()
    idx = {p.plant: p.index for p in data["plants"]}
    config = WorldConfig(
        level_id=1, width=50, height=50, total_ticks=500,
        seasons_enabled=True, animals_enabled=False, weather_enabled=False,
        season_schedule=LEVEL1_SEASONS,
    )
    sim = Simulator(
        config, data["plants"], animals=data["animals"],
        classifications=data["classifications_mapping"],
        unlocks={u.plant: u.unlock for u in data["unlocks"]},
    )
    actions = {499: [
        (idx["Grass"], 25, 25),
        (idx["Rose Bush"], 25, 26),
        (idx["Lavender"], 26, 25),
        (idx["Dwarf Sunflower"], 26, 26),
        (idx["Oak Tree"], 24, 25),
    ]}
    return sim.run(actions)


def test_reproduces_official_level1_statistics():
    r = _run_official_level1()
    assert abs(r.entropy - 0.4686790650623293) < 1e-12
    assert abs(r.density_factor - 0.002) < 1e-12
    assert abs(r.main_score - 0.0009373581301246587) < 1e-12
    assert abs(r.longevity_score - 4e-06) < 1e-12
    assert abs(r.final_score - 0.000750686504099727) < 1e-12
    assert r.occupied_cells == 5
    assert r.cmax == 2500
    assert r.leaderboard_score == 750687
