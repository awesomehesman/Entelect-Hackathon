from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LevelConfig:
    level_id: int
    width: int
    height: int
    total_ticks: int
    max_actions_per_tick: int = 20
    animals_enabled: bool | None = None
    weather_enabled: bool | None = None
    world_events_enabled: bool | None = None
    seasons_enabled: bool = True
    season_schedule: tuple[tuple[int, str], ...] = ((0, "Spring"),)
    weather_schedule: tuple[dict[str, object], ...] = ()
    event_schedule: tuple[dict[str, object], ...] = ()
    initial_species: frozenset[str] = frozenset()
    alpha: float | None = None
    k: float | None = None
    evaluator_scale: float | None = None
    submission_field: str = "index"

    @property
    def rows(self) -> int:
        return self.height

    @property
    def columns(self) -> int:
        return self.width

    @property
    def maximum_cells(self) -> int:
        return self.width * self.height

    def season_at(self, tick: int) -> str:
        from photospheria.simulation.seasons import season_at

        return season_at(self.season_schedule, tick, self.total_ticks)