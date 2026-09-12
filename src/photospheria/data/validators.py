from __future__ import annotations

from collections import Counter

from photospheria.data.models import AnimalDefinition, ClassificationGroup, PlantDefinition, UnlockDefinition
from photospheria.exceptions import ValidationError

EXPECTED_COUNTS = {
    "plants": 31,
    "unlocks": 26,
    "animals": 10,
    "classifications": 15,
}


def validate_authoritative_dataset(
    plants: list[PlantDefinition],
    unlocks: list[UnlockDefinition],
    animals: list[AnimalDefinition],
    classifications: list[ClassificationGroup],
) -> None:
    if len(plants) != EXPECTED_COUNTS["plants"]:
        raise ValidationError(f"Expected {EXPECTED_COUNTS['plants']} plants, got {len(plants)}.")

    plant_names = [plant.plant for plant in plants]
    if len(set(plant_names)) != len(plant_names):
        duplicate_names = sorted(name for name, count in Counter(plant_names).items() if count > 1)
        raise ValidationError(f"Duplicate plant names: {duplicate_names}")

    indices = [plant.index for plant in plants]
    if len(set(indices)) != len(indices):
        duplicate_indices = sorted(index for index, count in Counter(indices).items() if count > 1)
        raise ValidationError(f"Duplicate plant indices: {duplicate_indices}")
    if sorted(indices) != list(range(1, EXPECTED_COUNTS["plants"] + 1)):
        raise ValidationError(f"Plant indices must be contiguous 1..{EXPECTED_COUNTS['plants']}; got {sorted(indices)}")

    if len(unlocks) != EXPECTED_COUNTS["unlocks"]:
        raise ValidationError(f"Expected {EXPECTED_COUNTS['unlocks']} unlock definitions, got {len(unlocks)}.")

    if len(animals) != EXPECTED_COUNTS["animals"]:
        raise ValidationError(f"Expected {EXPECTED_COUNTS['animals']} animals, got {len(animals)}.")

    if len(classifications) != EXPECTED_COUNTS["classifications"]:
        raise ValidationError(f"Expected {EXPECTED_COUNTS['classifications']} classification groups, got {len(classifications)}.")

    # Validate classification group members are known plant species.
    known_plants = set(plant_names)
    for group in classifications:
        unknown_members = [member for member in group.members if member not in known_plants]
        if unknown_members:
            raise ValidationError(f"Classification group '{group.name}' contains unknown species: {unknown_members}")

    # Validate unlock names exist.
    for unlock in unlocks:
        if unlock.plant not in known_plants:
            raise ValidationError(f"Unlock target '{unlock.plant}' is not a known plant.")

    # Validate initial availability is not misrepresented in data validators.
    initial_species = {"Grass", "Rose Bush", "Lavender", "Dwarf Sunflower", "Oak Tree"}
    if not initial_species.issubset(known_plants):
        raise ValidationError("Initial plant set is missing expected species.")
