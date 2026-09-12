from __future__ import annotations

from dataclasses import dataclass

from photospheria.exceptions import ValidationError


@dataclass(frozen=True)
class CellState:
    soil: int
    nutrients: float = 100.0
    dead_matter: bool = False
    plant: str | None = None
    shade: bool = False


def age_at_tick(birth_tick: int, current_tick: int) -> int:
    if birth_tick < 0 or current_tick < birth_tick:
        raise ValidationError("Tick values must be ordered and non-negative.")
    return current_tick - birth_tick


def is_mature(birth_tick: int, current_tick: int, time_to_maturity: int) -> bool:
    if time_to_maturity < 0:
        raise ValidationError("time_to_maturity must be non-negative.")
    return age_at_tick(birth_tick, current_tick) >= time_to_maturity


def deplete_nutrients(cell: CellState, amount: float = 1.0) -> CellState:
    if amount < 0:
        raise ValidationError("Nutrient depletion amount must be non-negative.")
    return CellState(cell.soil, max(0.0, cell.nutrients - amount), cell.dead_matter, cell.plant, cell.shade)


def regenerate_dead_matter(cell: CellState, amount: float = 1.0) -> CellState:
    if amount < 0:
        raise ValidationError("Regeneration amount must be non-negative.")
    nutrients = min(100.0, cell.nutrients + amount) if cell.dead_matter else cell.nutrients
    return CellState(cell.soil, nutrients, cell.dead_matter, cell.plant, cell.shade)


def validate_preferred_soil(cell: CellState, preferred_soil: list[int]) -> None:
    if cell.soil not in preferred_soil:
        raise ValidationError(f"Soil {cell.soil} is not preferred for this plant.")


def replace_plant(cell: CellState, plant: str) -> CellState:
    if not plant:
        raise ValidationError("Replacement plant must be non-empty.")
    return CellState(cell.soil, cell.nutrients, cell.dead_matter, plant, cell.shade)


def season_at_tick(schedule: list[dict[str, object]], tick: int) -> str | None:
    matches = [item for item in schedule if int(item["tick"]) <= tick]
    return str(max(matches, key=lambda item: int(item["tick"]))["season"]) if matches else None


def occurred_events(schedule: list[dict[str, object]], tick: int) -> frozenset[str]:
    return frozenset(str(item["event"]) for item in schedule if int(item["tick"]) <= tick)


def shade_cells(x: int, y: int, width: int, height: int, radius: int) -> frozenset[tuple[int, int]]:
    if radius < 0:
        raise ValidationError("Shade radius must be non-negative.")
    return frozenset(
        (target_x, target_y)
        for target_x in range(max(0, x - radius), min(width, x + radius + 1))
        for target_y in range(max(0, y - radius), min(height, y + radius + 1))
    )