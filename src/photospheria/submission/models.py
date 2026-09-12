from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlantAction:
    plant: str | int
    x: int
    y: int

    @classmethod
    def from_raw(cls, payload: dict[str, Any], serialization_mode: str) -> "PlantAction":
        key = "plant_index" if serialization_mode == "plant_index" else "index"
        if serialization_mode not in {"plant_index", "index"}:
            raise ValueError(f"Unsupported serialization mode: {serialization_mode!r}")
        if key not in payload:
            raise ValueError(f"Action requires {key!r} for serialization mode {serialization_mode!r}.")
        return cls(
            plant=payload[key],
            x=int(payload["x"]),
            y=int(payload["y"]),
        )

    def to_raw(self, serialization_mode: str) -> dict[str, Any]:
        if serialization_mode not in {"plant_index", "index"}:
            raise ValueError(f"Unsupported serialization mode: {serialization_mode!r}")
        return {serialization_mode: self.plant, "x": self.x, "y": self.y}


@dataclass(frozen=True)
class TickActions:
    actions: list[PlantAction] = field(default_factory=list)

    @classmethod
    def from_raw(cls, payload: list[dict[str, Any]] | dict[str, Any], serialization_mode: str) -> "TickActions":
        items = payload.get("actions", []) if isinstance(payload, dict) else payload
        return cls(actions=[PlantAction.from_raw(item, serialization_mode) for item in items])


@dataclass(frozen=True)
class Submission:
    version: int = 1
    seed: int | None = None
    serialization_mode: str = "plant_index"
    ticks: list[TickActions] = field(default_factory=list)

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> "Submission":
        if "ticks" not in payload:
            raise ValueError("Submission requires a 'ticks' list.")
        if "serialization_mode" not in payload:
            raise ValueError("Submission requires a 'serialization_mode'.")
        mode = str(payload["serialization_mode"])
        if mode not in {"plant_index", "index"}:
            raise ValueError(f"Unsupported serialization mode: {mode!r}")
        return cls(
            version=int(payload.get("version", 1)),
            seed=payload.get("seed"),
            serialization_mode=mode,
            ticks=[TickActions.from_raw(tick, mode) for tick in payload["ticks"]],
        )

    def to_raw(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "serialization_mode": self.serialization_mode,
            **({"seed": self.seed} if self.seed is not None else {}),
            "ticks": [{"actions": [action.to_raw(self.serialization_mode) for action in tick.actions]} for tick in self.ticks],
        }
