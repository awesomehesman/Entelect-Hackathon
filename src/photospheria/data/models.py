from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GrowthDefinition:
    time_to_maturity: int
    spread_rate: int
    spread_mechanism: str
    spread_type: str
    spread_range: int
    root_type: str
    invasiveness_rank: int
    conditional_modifiers: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class RuleDefinition:
    weaknesses: list[dict[str, Any]] = field(default_factory=list)
    special: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class PlantDefinition:
    plant: str
    index: int
    growth: GrowthDefinition
    preferred_soil: list[int]
    rules: RuleDefinition
    role: str | None = None

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "PlantDefinition":
        growth = payload["growth"]
        return cls(
            plant=payload["plant"],
            index=int(payload["index"]),
            growth=GrowthDefinition(
                time_to_maturity=int(growth["time_to_maturity"]),
                spread_rate=int(growth["spread_rate"]),
                spread_mechanism=str(growth["spread_mechanism"]),
                spread_type=str(growth["spread_type"]),
                spread_range=int(growth["spread_range"]),
                root_type=str(growth["root_type"]),
                invasiveness_rank=int(growth["invasiveness_rank"]),
                conditional_modifiers=list(growth.get("conditional_modifiers", [])),
            ),
            preferred_soil=[int(v) for v in payload.get("preferred_soil", [])],
            rules=RuleDefinition(
                weaknesses=list(payload.get("rules", {}).get("weaknesses", [])),
                special=list(payload.get("rules", {}).get("special", [])),
            ),
            role=payload.get("role"),
        )


@dataclass(frozen=True)
class UnlockDefinition:
    plant: str
    unlock: dict[str, Any]

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "UnlockDefinition":
        return cls(plant=str(payload["plant"]), unlock=dict(payload["unlock"]))


@dataclass(frozen=True)
class AnimalEffect:
    type: str
    target: str | None = None
    value: float | int | str | None = None
    mode: str | None = None

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "AnimalEffect":
        return cls(
            type=str(payload["type"]),
            target=payload.get("target"),
            value=payload.get("value"),
            mode=payload.get("mode"),
        )


@dataclass(frozen=True)
class AnimalDefinition:
    id: str
    name: str
    requirements: dict[str, Any]
    effects: list[AnimalEffect]

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "AnimalDefinition":
        return cls(
            id=str(payload["id"]),
            name=str(payload["name"]),
            requirements=dict(payload["requirements"]),
            effects=[AnimalEffect.from_raw(item) for item in payload.get("effects", [])],
        )


@dataclass(frozen=True)
class ClassificationGroup:
    name: str
    members: list[str]

    @classmethod
    def from_mapping(cls, name: str, members: list[str]) -> "ClassificationGroup":
        return cls(name=name, members=[str(member) for member in members])


@dataclass(frozen=True)
class WorldFeature:
    name: str
    active: bool = False


@dataclass(frozen=True)
class LevelDefinition:
    width: int
    height: int
    total_ticks: int
    soil_grid: list[list[int]]
    terrain_features: dict[str, Any] | None = None
    season_schedule: list[dict[str, Any]] = None
    event_schedule: list[dict[str, Any]] = None

    def __post_init__(self):
        object.__setattr__(self, "season_schedule", list(self.season_schedule or []))
        object.__setattr__(self, "event_schedule", list(self.event_schedule or []))
