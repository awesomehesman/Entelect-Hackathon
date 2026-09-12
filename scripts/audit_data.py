#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DIR = ROOT / "Artifacts" / "additional-resources"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def detect_cycles(graph: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    active: set[str] = set()
    cycle_nodes: set[str] = set()

    def dfs(node: str):
        visited.add(node)
        active.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in active:
                cycle_nodes.add(node)
                cycle_nodes.add(neighbor)
        active.remove(node)

    for node in sorted(graph):
        if node not in visited:
            dfs(node)
    return cycle_nodes


def main() -> int:
    plants = load_json(RESOURCE_DIR / "plant_dataset.json")
    unlocks = load_json(RESOURCE_DIR / "plant_unlock_conditions.json")
    animals = load_json(RESOURCE_DIR / "animals.json")
    classifications = load_json(RESOURCE_DIR / "classifications.json")

    plant_names = [item["plant"] for item in plants]
    plant_indices = [item["index"] for item in plants]
    all_plants = {item["plant"] for item in plants}
    all_animals = {item["name"] for item in animals}
    classification_names = set(classifications.keys())

    duplicate_names = sorted({name for name in plant_names if plant_names.count(name) > 1})
    duplicate_indices = sorted({idx for idx in plant_indices if plant_indices.count(idx) > 1})
    invalid_index_range = sorted(set(plant_indices) - set(range(1, len(plants) + 1)))

    warnings: list[str] = []
    missing_unlock_targets: list[str] = []
    unknown_unlock_refs: list[tuple[str, str]] = []
    unknown_class_members: list[tuple[str, str]] = []
    condition_ops: set[str] = set()
    weakness_types: set[str] = set()
    special_types: set[str] = set()
    dependency_graph: dict[str, list[str]] = defaultdict(list)

    # Check unlock plant target coverage.
    for unlock in unlocks:
        plant = unlock["plant"]
        if plant not in all_plants:
            missing_unlock_targets.append(plant)

        def walk(node):
            if isinstance(node, dict):
                if "operator" in node:
                    condition_ops.add(str(node["operator"]))
                if "op" in node:
                    condition_ops.add(str(node["op"]))
                if "plant" in node and isinstance(node["plant"], str):
                    if node["plant"] not in all_plants:
                        unknown_unlock_refs.append((plant, node["plant"]))
                    else:
                        dependency_graph[plant].append(node["plant"])
                if "species" in node and isinstance(node["species"], str):
                    if node["species"] not in all_plants and node["species"] not in all_animals:
                        unknown_unlock_refs.append((plant, f"species:{node['species']}"))
                for value in node.values():
                    if isinstance(value, (list, dict)):
                        walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(unlock["unlock"])

    for plant in plants:
        for weakness in plant.get("rules", {}).get("weaknesses", []):
            weakness_types.add(weakness.get("type", ""))
        for special in plant.get("rules", {}).get("special", []):
            special_types.add(special.get("type", ""))

    for group_name, members in classifications.items():
        for member in members:
            if member not in all_plants:
                unknown_class_members.append((group_name, member))

    if "Shallow-root Species" in classification_names:
        warnings.append("Classification name mismatch: Shallow-root Species exists in runtime references but is not defined in classifications.json")
    if "Shallowroot Species" in classification_names:
        warnings.append("Classification name mismatch: Shallowroot Species exists in classifications.json but may not match the source animal references")

    cycles = detect_cycles(dict(dependency_graph))

    print("Photospheria data audit")
    print("=" * 24)
    print(f"Plant entries: {len(plants)}")
    print(f"Unlock entries: {len(unlocks)}")
    print(f"Animal entries: {len(animals)}")
    print(f"Classification groups: {len(classifications)}")
    print(f"Unique plant names: {len(set(plant_names)) == len(plant_names)}")
    print(f"Unique indices: {len(set(plant_indices)) == len(plant_indices)}")
    print(f"Indices 1..31 contiguous: {sorted(plant_indices) == list(range(1, 32))}")
    print(f"Duplicate names: {duplicate_names or 'none'}")
    print(f"Duplicate indices: {duplicate_indices or 'none'}")
    print(f"Invalid index range: {invalid_index_range or 'none'}")
    print(f"Missing unlock targets: {missing_unlock_targets or 'none'}")
    print(f"Unknown unlock refs: {unknown_unlock_refs or 'none'}")
    print(f"Unknown classification members: {unknown_class_members or 'none'}")
    print(f"Condition operators: {sorted(condition_ops) or 'none'}")
    print(f"Weakness types: {sorted(weakness_types) or 'none'}")
    print(f"Special types: {sorted(special_types) or 'none'}")
    print(f"Unlock cycles: {sorted(cycles) or 'none'}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f" - {warning}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
