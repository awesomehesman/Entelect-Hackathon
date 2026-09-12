from __future__ import annotations

from photospheria.data.loaders import load_challenge_data


def test_authoritative_data_pipeline_loads_expected_structure() -> None:
    payload = load_challenge_data()

    assert len(payload["plants"]) == 31
    assert len(payload["unlocks"]) == 26
    assert len(payload["animals"]) == 10
    assert len(payload["classifications"]) == 15

    plant_names = {plant.plant for plant in payload["plants"]}
    assert {"Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree"}.issubset(plant_names)

    groups = {group.name for group in payload["classifications"]}
    assert "Shallowroot Species" in groups
    assert "Deep-root Species" in groups