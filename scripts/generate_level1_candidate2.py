#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photospheria.levels.level1 import INITIAL_LEVEL1_SPECIES, Level1Constraints
from photospheria.scoring import diversity_entropy, final_score, longevity_score, main_score


def build_candidate(resource_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    plants = json.loads(resource_path.read_text(encoding="utf-8"))
    indices = {str(item["plant"]): int(item["index"]) for item in plants}
    ordered_species = ("Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree")
    if set(ordered_species) != INITIAL_LEVEL1_SPECIES:
        raise ValueError("Candidate species must equal the five initial Level 1 species.")
    constraints = Level1Constraints()
    placements: list[tuple[int, str, int, int]] = []
    zone_starts = {"Grass": 0, "Rose Bush": 8, "Lavender": 16, "Dwarf Sunflower": 24, "Oak Tree": 42}
    species_sequence = [species for species in ordered_species for _ in range(396)]
    for position, species in enumerate(species_sequence):
        zone_position = position % 396
        row = zone_starts[species] + zone_position // constraints.width
        col = zone_position % constraints.width
        tick = 401 + position // constraints.max_actions_per_tick
        constraints.validate_action(tick, row, col, species, set(ordered_species))
        placements.append((tick, species, row, col))

    grouped: dict[int, list[dict[str, int]]] = {}
    for tick, species, row, col in placements:
        grouped.setdefault(tick, []).append({"plant_index": indices[species], "row": row, "col": col})
    candidate = {"actions": [{"tick": tick, "plants": grouped[tick]} for tick in sorted(grouped)]}
    counts = {species: 396 for species in ordered_species}
    entropy = diversity_entropy(counts, 31)
    occupancy = 1980 / 2500
    lifespans = [500 - tick for tick, _, _, _ in placements]
    average_lifespan = {
        species: sum(500 - tick for tick, candidate, _, _ in placements if candidate == species) / 396
        for species in ordered_species
    }
    grass_rows = range(0, 8)
    oak_rows = range(42, 50)
    dwarf_rows = range(24, 32)
    grass_oak_min_distance = min(abs(grass_row - oak_row) for grass_row in grass_rows for oak_row in oak_rows)
    oak_radius = 4
    grass_in_oak_shade = sum(
        1 for row in grass_rows for col in range(50)
        if any(abs(row - oak_row) <= oak_radius and col == oak_col for oak_row in oak_rows for oak_col in range(50))
    )
    dwarf_in_oak_shade = sum(
        1 for row in dwarf_rows for col in range(50)
        if any(abs(row - oak_row) <= oak_radius and col == oak_col for oak_row in oak_rows for oak_col in range(50))
    )
    combined = final_score(main_score(entropy, 1980, 2500, alpha=1.0), longevity_score(lifespans, 500, 2500, k=1.0))
    diagnostics = {
        "candidate": "Level 1 Candidate 02",
        "strategy": "late survival-safe five-zone stripes with Oak last; no-spread fallback",
        "explicit_placements": len(placements),
        "tick_range": [min(item[0] for item in placements), max(item[0] for item in placements)],
        "actions_per_tick": {str(tick): len(actions) for tick, actions in grouped.items()},
        "target_cells": "1980 deterministic zone coordinates; 520 intentional buffer cells remain unused",
        "expected_final_counts_no_spread": counts,
        "expected_occupancy_no_spread": occupancy,
        "expected_entropy": entropy,
        "expected_main_score_alpha_1": main_score(entropy, 1980, 2500, alpha=1.0),
        "expected_longevity_score_k_1": longevity_score(lifespans, 500, 2500, k=1.0),
        "predicted_final_score_k_1_alpha_1": combined,
        "predicted_leaderboard_score_1e9_scale": round(combined * 1_000_000_000),
        "confirmed_components": {"occupancy": 1980 / 2500, "entropy": entropy, "main_score_alpha_1": main_score(entropy, 1980, 2500, alpha=1.0)},
        "hypothetical_k_1_components": {"longevity_score": longevity_score(lifespans, 500, 2500, k=1.0), "combined_score": combined},
        "expected_average_lifespan_k_1_by_species": average_lifespan,
        "exposure_ticks": {"minimum": min(lifespans), "maximum": max(lifespans), "average": sum(lifespans) / len(lifespans)},
        "zone_layout": {species: {"row_start": zone_starts[species], "row_count": 8, "cells": 396} for species in ordered_species},
        "intentional_unused_cells": 520,
        "shade_risk": {
            "oak_shade_radius": oak_radius,
            "minimum_grass_oak_row_distance": grass_oak_min_distance,
            "grass_target_cells_in_possible_oak_shade": grass_in_oak_shade,
            "dwarf_sunflower_target_cells_in_possible_oak_shade": dwarf_in_oak_shade,
            "dwarf_oak_boundary": "ten unused buffer rows separate Dwarf Sunflower and Oak; possible Oak shade reaches zero Dwarf Sunflower rows",
        },
        "old_candidate_comparison": {"placements": 2500, "ticks": [375, 499], "occupancy": 1.0, "risk": "early placements could reach the nutrient death boundary"},
        "new_candidate_comparison": {"placements": 1980, "ticks": [401, 499], "occupancy": 1980 / 2500, "risk_reduction": "every explicit exposure is strictly below 100 ticks"},
        "risks": ["unknown terrain/soil may reject placements", "natural spread and tick ordering are not modeled", "lower occupancy ceiling than the old candidate", "Oak shade semantics remain evaluator-dependent"],
    }
    return candidate, diagnostics


def generate() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[1]
    candidate, diagnostics = build_candidate(root / "Artifacts" / "additional-resources" / "plant_dataset.json")
    output_dir = root / "output" / "level1" / "candidate-02"
    output_dir.mkdir(parents=True, exist_ok=True)
    solution = output_dir / "solution.json"
    report = output_dir / "diagnostics.json"
    solution.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    report.write_text(json.dumps(diagnostics, indent=2) + "\n", encoding="utf-8")
    return solution, report


if __name__ == "__main__":
    for path in generate():
        print(path)