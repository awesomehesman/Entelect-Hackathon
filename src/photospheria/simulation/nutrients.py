from __future__ import annotations

from photospheria.core.models import Cell


def drain_occupied_cell(cell: Cell, amount: float = 1.0) -> bool:
    cell.nutrients = max(0.0, cell.nutrients - amount)
    return cell.nutrients == 0


def regenerate_dead_matter(cell: Cell, amount: float = 1.0) -> None:
    if cell.dead_matter:
        cell.nutrients = min(100.0, cell.nutrients + amount)