from __future__ import annotations

from photospheria.exceptions import AmbiguousMechanicError


def resolve_classification(name: str, classifications: dict[str, list[str]], *, strict: bool = True) -> list[str]:
    if name in classifications:
        return classifications[name]
    if name == "Shallow-root Species" and "Shallowroot Species" in classifications:
        if strict:
            raise AmbiguousMechanicError("AMB-002", "The source uses both Shallow-root Species and Shallowroot Species.")
        return classifications["Shallowroot Species"]
    raise KeyError(name)