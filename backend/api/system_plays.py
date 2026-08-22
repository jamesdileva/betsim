"""System Plays calibration endpoint: is your stated probability realistic?"""

from typing import Annotated

import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.system_plays import save_calibration_result
from schemas.ml_model import SystemPlayResultCreate
from schemas.system_plays import CalibrationReport, SystemPlaysRequest

router = APIRouter()

# 95% two-sided z-score for the calibration tolerance band
_Z = 1.96

# cap total Bernoulli draws to keep latency bounded
_MAX_DRAWS = 1_000_000


def _recommendation(status: str, error: float) -> str:
    if status == "well_calibrated":
        return "Your probability estimates are well-calibrated. Keep tracking."
    direction = "overestimates" if status == "overconfident" else "underestimates"
    return f"Your model {direction} probability by ~{error:.1%}. Consider adjusting."


@router.post("/system-plays", response_model=CalibrationReport)
def calibrate(request: SystemPlaysRequest, db: Annotated[Session, Depends(get_db)]):
    """Compare the stated win probability against simulated reality.

    Draws are generated *at* the stated probability, so any gap is pure
    sampling variance — this shows how much noise to expect at this sample
    size and flags estimates that fall outside statistical tolerance.
    """
    stated = request.win_probability
    rng = np.random.default_rng(request.seed)
    n_draws = min(request.num_simulations * request.num_bets, _MAX_DRAWS)
    wins = int((rng.random(n_draws) < stated).sum())
    actual = wins / n_draws
    error = abs(actual - stated)

    standard_error = float(np.sqrt(stated * (1.0 - stated) / n_draws))
    tolerance = _Z * standard_error
    ci_low = max(0.0, actual - tolerance)
    ci_high = min(1.0, actual + tolerance)

    if error <= tolerance:
        status = "well_calibrated"
    elif actual < stated:
        status = "overconfident"
    else:
        status = "underconfident"

    report = CalibrationReport(
        stated_probability=stated,
        actual_win_rate=actual,
        calibration_error=error,
        calibration_status=status,
        confidence_interval_low=ci_low,
        confidence_interval_high=ci_high,
        recommendation=_recommendation(status, error),
    )

    save_calibration_result(
        db,
        SystemPlayResultCreate(
            stated_probability=report.stated_probability,
            actual_win_rate=report.actual_win_rate,
            calibration_error=report.calibration_error,
            calibration_status=status,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            recommendation=report.recommendation,
        ),
    )
    return report

