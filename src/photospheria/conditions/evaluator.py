from __future__ import annotations

from typing import Any

from photospheria.exceptions import AmbiguousMechanicError, ConditionEvaluationError


def _coerce_numeric(value: Any, *, field_name: str, node: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    raise ConditionEvaluationError(f"{field_name} condition requires numeric value in {node!r}.")


def _node_type(node: Any) -> str:
    if not isinstance(node, dict):
        return ""
    return str(node.get("type") or node.get("op") or "").lower()


def _children(node: dict[str, Any]) -> list[Any]:
    conditions = node.get("conditions")
    if isinstance(conditions, list):
        return conditions
    children = node.get("children")
    if isinstance(children, list):
        return children
    return []


def _compare(value: float, operator: str, threshold: float) -> bool:
    mapping = {
        ">": value > threshold,
        ">=": value >= threshold,
        "<": value < threshold,
        "<=": value <= threshold,
        "==": value == threshold,
        "!=": value != threshold,
    }
    if operator not in mapping:
        raise ConditionEvaluationError(f"Unsupported comparison operator: {operator!r}")
    return mapping[operator]


def _resolve_species(node: dict[str, Any], *, allow_group: bool = False) -> str | list[str] | None:
    species = node.get("species")
    if species is not None:
        return species
    plant_name = node.get("plant")
    if plant_name is not None:
        return plant_name
    if allow_group:
        group = node.get("species_group")
        if group is not None:
            return group
    return None


def _species_group_total(node: dict[str, Any], ctx: dict[str, Any]) -> float:
    group = node.get("species_group") or node.get("group") or node.get("species")
    if isinstance(group, str):
        if group in ctx.get("species_groups", {}):
            members = ctx["species_groups"][group]
            return float(sum(float(ctx.get("species_count", {}).get(member, 0)) for member in members))
        return float(ctx.get("species_count", {}).get(group, 0))
    if isinstance(group, list):
        return float(sum(float(ctx.get("species_count", {}).get(member, 0)) for member in group))
    raise ConditionEvaluationError(f"Invalid species group in condition: {node!r}")


def _coverage_total(node: dict[str, Any], ctx: dict[str, Any]) -> float:
    target = _resolve_species(node, allow_group=True)
    coverage = ctx.get("coverage", {})
    if isinstance(target, str):
        return float(coverage.get(target, 0.0))
    if isinstance(target, list):
        return float(sum(float(coverage.get(item, 0.0)) for item in target))
    raise ConditionEvaluationError(f"coverage condition requires a species or species group: {node!r}")


def evaluate_condition(node: Any, context: dict[str, Any] | None = None) -> bool:
    """Safely evaluate a boolean condition tree for an unlock or effect.

    This is intentionally strict. Any mechanic documented as unresolved in the
    challenge materials must raise AmbiguousMechanicError instead of guessing.
    """
    ctx = context or {}
    if node is None:
        return True
    if isinstance(node, bool):
        return node

    if not isinstance(node, dict):
        raise ConditionEvaluationError(f"Unsupported condition node: {node!r}")

    node_type = _node_type(node)
    if node_type in {"and", "or", "not"}:
        relation = node_type.upper()
        conditions = _children(node)
        if relation == "AND":
            return all(evaluate_condition(item, ctx) for item in conditions)
        if relation == "OR":
            return any(evaluate_condition(item, ctx) for item in conditions)
        if relation == "NOT":
            if len(conditions) != 1:
                raise ConditionEvaluationError("NOT conditions require exactly one child condition.")
            return not evaluate_condition(conditions[0], ctx)

    if node_type in {"species_present", "species_absent"}:
        species = _resolve_species(node)
        if species is None:
            raise ConditionEvaluationError(f"{node_type} condition requires a species name.")
        present = bool(ctx.get("species_present", {}).get(species, False))
        if node_type == "species_present":
            return present
        return not present

    if node_type == "group_coverage":
        threshold = _coerce_numeric(node.get("threshold", node.get("value", 0.0)), field_name="group_coverage", node=node)
        operator = str(node.get("operator", ">="))
        value = _species_group_total(node, ctx)
        return _compare(value, operator, threshold)

    if node_type == "coverage":
        species = _resolve_species(node, allow_group=True)
        if species is None:
            raise ConditionEvaluationError("coverage condition requires species or species_group.")
        threshold = _coerce_numeric(node.get("threshold", node.get("value", 0.0)), field_name="coverage", node=node)
        operator = str(node.get("operator", ">="))
        value = _coverage_total(node, ctx)
        return _compare(value, operator, threshold)

    if node_type == "count":
        threshold = _coerce_numeric(node.get("threshold", node.get("value", 0.0)), field_name="count", node=node)
        operator = str(node.get("operator", ">="))
        target = _resolve_species(node, allow_group=True)
        if isinstance(target, str):
            value = float(ctx.get("species_count", {}).get(target, 0))
        elif isinstance(target, list):
            value = float(sum(float(ctx.get("species_count", {}).get(item, 0)) for item in target))
        else:
            raise ConditionEvaluationError("count condition requires species or species_group.")
        return _compare(value, operator, threshold)

    if node_type in {"feature_count", "feature"}:
        raise AmbiguousMechanicError("AMB-013", "feature_count semantics are unresolved where fractional values appear in challenge data.")

    if node_type == "dominance":
        raise AmbiguousMechanicError("AMB-014", "dominance semantics are intentionally unresolved until the official simulation order is confirmed.")

    if node_type == "event":
        event_name = node.get("event")
        if event_name is None:
            raise ConditionEvaluationError("event condition requires an event name.")
        return bool(ctx.get("events", {}).get(event_name, False))

    if node_type == "animal_present":
        animal = node.get("animal")
        return bool(ctx.get("animals", {}).get(animal, False))

    if node_type == "animal_absent":
        animal = node.get("animal")
        return not bool(ctx.get("animals", {}).get(animal, False))

    raise ConditionEvaluationError(f"Unsupported condition type: {node_type!r}")
