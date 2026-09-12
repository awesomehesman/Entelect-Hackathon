from __future__ import annotations

from photospheria.core.models import PlantInstance


def age_at(instance: PlantInstance, tick: int) -> int:
    return instance.age_at(tick)


def is_mature(instance: PlantInstance, tick: int) -> bool:
    return instance.is_mature(tick)