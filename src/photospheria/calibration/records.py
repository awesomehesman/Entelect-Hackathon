from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationValue:
    value: object
    status: str
    evidence: str


@dataclass(frozen=True)
class LevelCalibration:
    level_id: int
    alpha: CalibrationValue
    k: CalibrationValue
    evaluator_scale: CalibrationValue
    submission_field: CalibrationValue


LEVEL1_CALIBRATION = LevelCalibration(
    level_id=1,
    alpha=CalibrationValue(1.0, "observed/inferred-from-official-output", "Calibration 01 main score equation"),
    k=CalibrationValue(1.0, "suspected", "Calibration 01 longevity value; not uniquely identified"),
    evaluator_scale=CalibrationValue(1_000_000_000, "observed-approximation", "Official leaderboard score"),
    submission_field=CalibrationValue("plant_index", "observed", "Calibration 01 accepted successfully"),
)