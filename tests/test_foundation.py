from photospheria.conditions.evaluator import evaluate_condition
from photospheria.data.loaders import load_challenge_data


def test_challenge_data_loads_and_has_expected_counts():
    payload = load_challenge_data()
    assert len(payload["plants"]) == 31
    assert len(payload["unlocks"]) == 26
    assert len(payload["animals"]) == 10
    assert len(payload["classifications"]) == 15


def test_simple_condition_evaluation_works():
    assert evaluate_condition({"type": "AND", "conditions": [{"type": "count", "species": "Grass", "threshold": 1, "operator": ">="}, {"type": "event", "event": "Rain"}]}, {"species_count": {"Grass": 3}, "events": {"Rain": True}}) is True
    assert evaluate_condition({"type": "NOT", "conditions": [{"type": "event", "event": "Ash Eclipse"}]}, {"events": {"Ash Eclipse": False}}) is True
