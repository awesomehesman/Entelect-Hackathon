from __future__ import annotations

from typing import Any

from photospheria.conditions.evaluator import evaluate_condition
from photospheria.exceptions import AmbiguousMechanicError


def evaluate_animal_requirements(requirements: dict[str, Any], context: dict[str, Any]) -> bool:
    groups = context.get("species_groups", {})
    if "Shallow-root Species" not in groups and "Shallow-root Species" in str(requirements):
        raise AmbiguousMechanicError("AMB-002", "Animal data refers to Shallow-root Species, while the classification data defines Shallowroot Species.")
    return evaluate_condition(requirements, context)