from __future__ import annotations

import pytest

from photospheria.exceptions import AmbiguousMechanicError, ValidationError
from photospheria.conditions.animals import evaluate_animal_requirements
from photospheria.submission.models import Submission
from photospheria.submission.validator import validate_submission


def test_serialization_modes_are_mandatory_and_round_trip() -> None:
    with pytest.raises(ValueError):
        Submission.model_validate({"ticks": []})
    payload = {"serialization_mode": "index", "ticks": [{"actions": [{"index": 1, "x": 0, "y": 0}]}]}
    assert Submission.model_validate(payload).to_raw() == {"version": 1, **payload}
    payload["serialization_mode"] = "plant_index"
    payload["ticks"][0]["actions"][0] = {"plant_index": 1, "x": 0, "y": 0}
    assert Submission.model_validate(payload).to_raw() == {"version": 1, **payload}


def test_submission_rejects_action_and_world_range_errors() -> None:
    submission = Submission.model_validate({"serialization_mode": "index", "ticks": [{"actions": [{"index": 99, "x": 0, "y": 0}]}]})
    with pytest.raises(ValidationError):
        validate_submission(submission, plant_indices={1}, width=3, height=3, total_ticks=1)

    out_of_bounds = Submission.model_validate({"serialization_mode": "index", "ticks": [{"actions": [{"index": 1, "x": 3, "y": 0}]}]})
    with pytest.raises(ValidationError):
        validate_submission(out_of_bounds, plant_indices={1}, width=3, height=3, total_ticks=1)

    out_of_range_tick = Submission.model_validate({"serialization_mode": "index", "ticks": [{"actions": []}, {"actions": []}]})
    with pytest.raises(ValidationError):
        validate_submission(out_of_range_tick, total_ticks=1)

    too_many = Submission(serialization_mode="index", ticks=[type(submission.ticks[0])(actions=[submission.ticks[0].actions[0]] * 21)])
    with pytest.raises(ValidationError):
        validate_submission(too_many)


def test_required_unresolved_mechanics_have_explicit_guards() -> None:
    from photospheria.conditions.ambiguity import require_resolved_mechanic

    for amb_id in {"AMB-004", "AMB-006", "AMB-008", "AMB-009", "AMB-011", "AMB-012", "AMB-014", "AMB-018"}:
        with pytest.raises(AmbiguousMechanicError) as error:
            require_resolved_mechanic(amb_id)
        assert error.value.amb_id == amb_id


def test_animal_classification_mismatch_is_not_normalized() -> None:
    with pytest.raises(AmbiguousMechanicError) as error:
        evaluate_animal_requirements(
            {"type": "count", "species_group": "Shallow-root Species", "threshold": 25, "operator": ">="},
            {"species_groups": {"Shallowroot Species": ["Rose Bush"]}, "species_count": {"Rose Bush": 25}},
        )
    assert error.value.amb_id == "AMB-002"