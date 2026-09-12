from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from photospheria.exceptions import ValidationError
from photospheria.levels.base import LevelConfig

INITIAL_LEVEL1_SPECIES = frozenset({"Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree"})
LEVEL1_WEATHER_EVENTS = frozenset({"Rain", "Drought", "Ash Eclipse", "Earthquake"})
LEVEL1_SEASON_SCHEDULE = ((0, "Spring"), (100, "Summer"), (200, "Autumn"), (300, "Winter"), (400, "Spring"))


@dataclass(frozen=True)
class Level1Constraints(LevelConfig):
    level_id: int = 1
    width: int = 50
    height: int = 50
    total_ticks: int = 500
    max_actions_per_tick: int = 20
    animals_enabled: bool = False
    weather_enabled: bool = False
    world_events_enabled: bool = False
    seasons_enabled: bool = True
    season_schedule: tuple[tuple[int, str], ...] = LEVEL1_SEASON_SCHEDULE
    initial_species: frozenset[str] = INITIAL_LEVEL1_SPECIES
    alpha: float = 1.0
    submission_field: str = "plant_index"

    @staticmethod
    def season_at(tick: int) -> str:
        if not 0 <= tick < 500:
            raise ValidationError(f"Tick must be in 0..499: {tick}")
        return max((entry for entry in LEVEL1_SEASON_SCHEDULE if entry[0] <= tick), key=lambda entry: entry[0])[1]

    def validate_action(self, tick: int, row: int, col: int, plant: str, unlocked_species: set[str]) -> None:
        if not 0 <= tick < self.total_ticks:
            raise ValidationError(f"Tick must be in 0..{self.total_ticks - 1}: {tick}")
        if not 0 <= row < self.height or not 0 <= col < self.width:
            raise ValidationError(f"Coordinates must be in rows 0..{self.height - 1} and cols 0..{self.width - 1}.")
        if plant not in unlocked_species:
            raise ValidationError(f"Plant is not currently unlocked: {plant}")

    def validate_tick_action_count(self, count: int) -> None:
        if not 0 <= count <= self.max_actions_per_tick:
            raise ValidationError(f"A tick may contain at most {self.max_actions_per_tick} actions.")


class Reachability(str, Enum):
    DEFINITELY_REACHABLE = "A"
    DEFINITELY_UNREACHABLE = "B"
    CONDITIONAL_UNKNOWN = "C"


@dataclass(frozen=True)
class SpeciesReachability:
    species: str
    status: Reachability
    reason: str


def _leaf_status(node: dict[str, Any], statuses: dict[str, Reachability], animal_names: set[str]) -> tuple[Reachability, str]:
    node_type = str(node.get("type", "")).lower()
    if node_type == "event":
        return Reachability.DEFINITELY_UNREACHABLE, "requires a weather/world event disabled in Level 1"
    if node_type == "feature_count":
        return Reachability.CONDITIONAL_UNKNOWN, "depends on unresolved feature-count semantics and unknown world features"
    if node_type == "species_present":
        species = str(node.get("species", ""))
        if species in animal_names:
            return Reachability.DEFINITELY_UNREACHABLE, f"requires disabled animal {species}"
        return statuses.get(species, Reachability.CONDITIONAL_UNKNOWN), f"depends on species {species}"
    if node_type == "species_absent":
        species = str(node.get("species", ""))
        if species in animal_names:
            return Reachability.DEFINITELY_REACHABLE, f"disabled animal {species} is absent"
        return Reachability.CONDITIONAL_UNKNOWN, f"absence of plant {species} is not established"
    if node_type in {"coverage", "count", "group_coverage", "dominance"}:
        referenced = node.get("plant") or node.get("species")
        if isinstance(referenced, str) and referenced in statuses:
            if statuses[referenced] == Reachability.DEFINITELY_UNREACHABLE:
                return Reachability.DEFINITELY_UNREACHABLE, f"requires unavailable plant {referenced}"
        referenced_group = node.get("species_group")
        if isinstance(referenced_group, list):
            if any(statuses.get(item) == Reachability.DEFINITELY_UNREACHABLE for item in referenced_group):
                return Reachability.CONDITIONAL_UNKNOWN, "group condition may be satisfiable through another member"
        return Reachability.CONDITIONAL_UNKNOWN, f"requires unresolved world state: {node_type}"
    return Reachability.CONDITIONAL_UNKNOWN, f"unsupported or undocumented condition: {node_type or 'missing type'}"


def _condition_status(node: dict[str, Any], statuses: dict[str, Reachability], animal_names: set[str]) -> tuple[Reachability, str]:
    operation = str(node.get("op") or node.get("type") or "").upper()
    if operation in {"AND", "OR"}:
        children = node.get("children", node.get("conditions", []))
        results = [_condition_status(child, statuses, animal_names) for child in children]
        if operation == "AND":
            if any(status == Reachability.DEFINITELY_UNREACHABLE for status, _ in results):
                return Reachability.DEFINITELY_UNREACHABLE, "contains a definitely unavailable requirement"
            if all(status == Reachability.DEFINITELY_REACHABLE for status, _ in results):
                return Reachability.DEFINITELY_REACHABLE, "all requirements are definitely reachable"
            return Reachability.CONDITIONAL_UNKNOWN, "contains a conditional or unknown requirement"
        if any(status == Reachability.DEFINITELY_REACHABLE for status, _ in results):
            return Reachability.DEFINITELY_REACHABLE, "an OR branch is definitely reachable"
        if all(status == Reachability.DEFINITELY_UNREACHABLE for status, _ in results):
            return Reachability.DEFINITELY_UNREACHABLE, "all OR branches are definitely unavailable"
        return Reachability.CONDITIONAL_UNKNOWN, "some OR branches remain conditional or unknown"
    if operation == "NOT":
        children = node.get("children", node.get("conditions"))
        child = children[0] if isinstance(children, list) else node.get("child")
        status, _ = _condition_status(child, statuses, animal_names)
        if status == Reachability.DEFINITELY_REACHABLE:
            return Reachability.DEFINITELY_UNREACHABLE, "negates a definitely reachable requirement"
        if status == Reachability.DEFINITELY_UNREACHABLE:
            return Reachability.DEFINITELY_REACHABLE, "negates a definitely unavailable requirement"
        return Reachability.CONDITIONAL_UNKNOWN, "negates a conditional or unknown requirement"
    return _leaf_status(node, statuses, animal_names)


def analyze_level1_reachability(
    plant_names: set[str],
    unlocks: list[dict[str, Any]],
    animal_names: set[str],
) -> dict[str, SpeciesReachability]:
    statuses = {name: Reachability.DEFINITELY_REACHABLE for name in INITIAL_LEVEL1_SPECIES}
    for name in plant_names - INITIAL_LEVEL1_SPECIES:
        statuses.setdefault(name, Reachability.CONDITIONAL_UNKNOWN)

    unlock_by_plant = {str(item["plant"]): item["unlock"] for item in unlocks}
    changed = True
    while changed:
        changed = False
        for species, condition in unlock_by_plant.items():
            status, _ = _condition_status(condition, statuses, animal_names)
            if status != statuses[species]:
                if statuses[species] == Reachability.CONDITIONAL_UNKNOWN or status == Reachability.DEFINITELY_UNREACHABLE:
                    statuses[species] = status
                    changed = True

    result: dict[str, SpeciesReachability] = {}
    for species in sorted(plant_names):
        if species in INITIAL_LEVEL1_SPECIES:
            result[species] = SpeciesReachability(species, Reachability.DEFINITELY_REACHABLE, "one of the five explicitly available starting species")
        else:
            status, reason = _condition_status(unlock_by_plant[species], statuses, animal_names)
            result[species] = SpeciesReachability(species, status, reason)
    return result


def build_level1_calibration_actions() -> tuple[tuple[int, str, int, int], ...]:
    """Return coordinate-valid initial-species actions; terrain validity is unknown."""
    placements = (("Grass", 2, 2), ("Rose Bush", 2, 47), ("Lavender", 47, 2), ("Dwarf Sunflower", 47, 47), ("Oak Tree", 25, 25))
    return tuple((0, species, row, col) for species, row, col in placements)