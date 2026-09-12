from __future__ import annotations

import pytest

from photospheria.calibration import LEVEL1_CALIBRATION
from photospheria.data.classifications import resolve_classification
from photospheria.exceptions import AmbiguousMechanicError
from photospheria.levels import LEVEL_2, LEVEL_3, LEVEL_4, LevelConfig, Level1Constraints
from photospheria.simulation.events import events_at
from photospheria.core.models import World
from photospheria.scoring import main_score_for_config
from photospheria.simulation.seasons import season_at


def test_level_config_drives_dimensions_and_cmax() -> None:
    assert (Level1Constraints().rows, Level1Constraints().columns, Level1Constraints().maximum_cells) == (50, 50, 2500)
    assert (LEVEL_2.rows, LEVEL_2.columns) == (70, 100)
    assert (LEVEL_3.rows, LEVEL_3.columns) == (150, 150)
    assert (LEVEL_4.rows, LEVEL_4.columns) == (200, 300)


def test_shared_season_and_event_engines_accept_configured_schedules() -> None:
    config = LevelConfig(9, 3, 4, 10, season_schedule=((0, "A"), (5, "B")))
    assert config.season_at(4) == "A"
    assert season_at(config.season_schedule, 5, config.total_ticks) == "B"
    assert events_at(({"tick": 5, "event": "Rain"},), 5)[0]["event"] == "Rain"


def test_shared_world_and_scoring_accept_level_config() -> None:
    config = LevelConfig(9, 3, 4, 10, alpha=1.0)
    world = World.from_config(config, [[0] * 3 for _ in range(4)])
    assert (world.width, world.height, world.total_ticks) == (3, 4, 10)
    assert main_score_for_config(1.0, 6, config) == pytest.approx(0.5)


def test_calibration_certainty_and_classification_ambiguity_are_centralized() -> None:
    assert LEVEL1_CALIBRATION.alpha.status.startswith("observed")
    assert LEVEL1_CALIBRATION.k.status == "suspected"
    with pytest.raises(AmbiguousMechanicError):
        resolve_classification("Shallow-root Species", {"Shallowroot Species": ["Rose Bush"]})