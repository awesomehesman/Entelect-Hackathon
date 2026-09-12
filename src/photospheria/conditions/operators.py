from __future__ import annotations

from typing import Any, Callable

from photospheria.exceptions import ConditionEvaluationError


def compare(lhs: Any, operator: str, rhs: Any) -> bool:
    if operator == ">":
        return lhs > rhs
    if operator == ">=":
        return lhs >= rhs
    if operator == "<":
        return lhs < rhs
    if operator == "<=":
        return lhs <= rhs
    if operator == "==":
        return lhs == rhs
    if operator == "!=":
        return lhs != rhs
    raise ConditionEvaluationError(f"Unsupported comparison operator: {operator!r}")


def all_conditions(values: list[bool]) -> bool:
    return all(values)


def any_conditions(values: list[bool]) -> bool:
    return any(values)


def not_condition(value: bool) -> bool:
    return not value
