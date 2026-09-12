from __future__ import annotations

import pytest

from photospheria.mechanics.safe import (
    CellState,
    age_at_tick,
    deplete_nutrients,
    is_mature,
    occurred_events,
    regenerate_dead_matter,
    replace_plant,
    season_at_tick,
    shade_cells,
    validate_preferred_soil,
)
from photospheria.exceptions import ValidationError


def test_safe_cell_mechanics_are_pure_and_deterministic() -> None:
    cell = CellState(soil=1, nutrients=1, dead_matter=True)
    assert age_at_tick(2, 5) == 3
    assert is_mature(2, 5, 3)
    assert deplete_nutrients(cell).nutrients == 0
    assert regenerate_dead_matter(cell).nutrients == 2
    assert replace_plant(cell, "Grass").plant == "Grass"
    validate_preferred_soil(cell, [0, 1])
    with pytest.raises(ValidationError):
        validate_preferred_soil(cell, [0])


def test_seasons_events_and_shade_use_explicit_schedules() -> None:
    assert season_at_tick([{"tick": 0, "season": "Spring"}, {"tick": 5, "season": "Summer"}], 6) == "Summer"
    assert occurred_events([{"tick": 2, "event": "Rain"}, {"tick": 8, "event": "Drought"}], 5) == {"Rain"}
    assert (0, 0) in shade_cells(1, 1, 3, 3, 1)
    assert (2, 2) in shade_cells(1, 1, 3, 3, 1)