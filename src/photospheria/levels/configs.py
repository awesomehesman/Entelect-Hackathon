"""Per-level world configuration for the simulator/generator.

Certainty of each field is documented. Confirmed values come from the two
official evaluation logs in SubmissionLogs/ and the problem statement. Where a
value is not confirmed, the source is marked and the value is a documented
assumption used only for local simulation and scheduling (the emitted action
list degrades gracefully if the real world differs).
"""

from __future__ import annotations

from photospheria.simulation.full_engine import WorldConfig

# Season schedules.
# Level 1 confirmed from its log: Summer@100, Autumn@200, Winter@300, Spring@400.
SEASONS_500 = ((0, "Spring"), (100, "Summer"), (200, "Autumn"), (300, "Winter"), (400, "Spring"))
# Level 4 confirmed from its log: season changes at 100/200/300/400/500/600/700.
SEASONS_800 = (
    (0, "Spring"), (100, "Summer"), (200, "Autumn"), (300, "Winter"),
    (400, "Spring"), (500, "Summer"), (600, "Autumn"), (700, "Winter"),
)
# Level 4 confirmed events from its log.
EVENTS_L4 = ((50, "Rain"), (250, "Ash Eclipse"), (280, "Drought"), (700, "Earthquake"))


def level_config(level_id: int) -> WorldConfig:
    if level_id == 1:
        # CONFIRMED (log): 50x50, T=500, animals/weather OFF, seasons ON.
        return WorldConfig(
            level_id=1, width=50, height=50, total_ticks=500,
            seasons_enabled=True, animals_enabled=False, weather_enabled=False,
            events_enabled=False, season_schedule=SEASONS_500,
        )
    if level_id == 2:
        # ASSUMED dims (repo): 100x70, T=500. Animals/weather ON (PDF: "critters
        # and elements"). Season schedule assumed = SEASONS_500. Events unknown.
        return WorldConfig(
            level_id=2, width=100, height=70, total_ticks=500,
            seasons_enabled=True, animals_enabled=True, weather_enabled=True,
            events_enabled=True, season_schedule=SEASONS_500,
        )
    if level_id == 3:
        # ASSUMED dims (repo): 150x150, T=800. Animals/weather/terrain/events ON
        # (PDF Level 3: unfriendly terrain + weather). Schedules assumed.
        return WorldConfig(
            level_id=3, width=150, height=150, total_ticks=800,
            seasons_enabled=True, animals_enabled=True, weather_enabled=True,
            events_enabled=True, season_schedule=SEASONS_800, event_schedule=EVENTS_L4,
        )
    if level_id == 4:
        # CONFIRMED (log): Cmax=60000 (200x300), T=800, full weather+events.
        return WorldConfig(
            level_id=4, width=200, height=300, total_ticks=800,
            seasons_enabled=True, animals_enabled=True, weather_enabled=True,
            events_enabled=True, season_schedule=SEASONS_800, event_schedule=EVENTS_L4,
        )
    raise ValueError(f"Unknown level: {level_id}")


# Field-certainty registry for documentation/diagnostics.
LEVEL_CERTAINTY = {
    1: {"dims": "confirmed(log)", "ticks": "confirmed(log)", "seasons": "confirmed(log)",
        "animals": "confirmed(off)", "weather": "confirmed(off)", "events": "confirmed(none)"},
    2: {"dims": "assumed(repo)", "ticks": "assumed(repo)", "seasons": "assumed",
        "animals": "confirmed(on)", "weather": "confirmed(on)", "events": "assumed"},
    3: {"dims": "assumed(repo)", "ticks": "assumed", "seasons": "assumed",
        "animals": "confirmed(on)", "weather": "confirmed(on)", "events": "assumed"},
    4: {"dims": "confirmed(log:200x300)", "ticks": "confirmed(log:800)", "seasons": "confirmed(log)",
        "animals": "confirmed(on)", "weather": "confirmed(on)", "events": "confirmed(log)"},
}
