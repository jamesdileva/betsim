"""RecommendationService: the Intelligence Score (Product Design section 9).

Score = probability(25) + simulation(25) + EV(25, sigmoid-scaled)
        + confidence(15) + calibration(10), plus bonuses:
  +5 strong positive EV (ev > 0.10), +3 well-calibrated model,
  +2 simulation agreeing with the prediction.
Stars: >=85 five, >=70 four, >=55 three, >=40 two, else one.
Risk level derives from simulated risk of ruin (the doc's EV-based mapping
contradicts its own "risk of ruin < 10%" definition — ruin is authoritative).
"""

import math
from dataclasses import dataclass


@dataclass
class IntelligenceScoreResult:
    score: int
    stars: int
    risk_level: str
    breakdown: dict[str, dict[str, float | str]]


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _stars_for(raw_score: float) -> int:
    if raw_score >= 85:
        return 5
    if raw_score >= 70:
        return 4
    if raw_score >= 55:
        return 3
    if raw_score >= 40:
        return 2
    return 1


def calculate_intelligence_score(
    *,
    predicted_prob: float,
    simulation_win_rate: float,
    ev: float,
    model_confidence: float,
    calibration_status: str,
    risk_of_ruin: float | None = None,
) -> IntelligenceScoreResult:
    """Aggregate a recommendation into a 0-100 Intelligence Score."""

    def clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    p = clamp01(predicted_prob)
    sim = clamp01(simulation_win_rate)
    confidence = clamp01(model_confidence)

    probability_points = p * 25.0
    simulation_points = sim * 25.0
    # +10% EV -> ~22 points; -10% EV -> ~3 points
    ev_points = _sigmoid(ev / 0.10) * 25.0
    confidence_points = confidence * 15.0
    well_calibrated = calibration_status == "well_calibrated"
    calibration_points = 10.0 if well_calibrated else 5.0

    raw = (
        probability_points
        + simulation_points
        + ev_points
        + confidence_points
        + calibration_points
    )

    bonus_total = 0.0
    bonuses: list[str] = []
    if ev > 0.10:
        raw += 5.0
        bonus_total += 5.0
        bonuses.append("strong_ev")
    if well_calibrated:
        raw += 3.0
        bonus_total += 3.0
        bonuses.append("calibration")
    if sim > p:
        raw += 2.0
        bonus_total += 2.0
        bonuses.append("simulation_agrees")

    score = round(min(raw, 100.0))

    if risk_of_ruin is None:
        risk_level = "Low" if score >= 70 else ("Medium" if score >= 40 else "High")
    elif risk_of_ruin < 0.10:
        risk_level = "Low"
    elif risk_of_ruin <= 0.25:
        risk_level = "Medium"
    else:
        risk_level = "High"

    def component(name: str, value: float | str, points: float, maximum: float) -> dict:
        return {"value": value, "points": round(points, 1), "max": maximum}

    return IntelligenceScoreResult(
        score=score,
        stars=_stars_for(score),
        risk_level=risk_level,
        breakdown={
            "probability": component("probability", round(p, 4), probability_points, 25),
            "simulation": component("simulation", round(sim, 4), simulation_points, 25),
            "ev": component("ev", round(ev, 4), ev_points, 25),
            "confidence": component("confidence", round(confidence, 4), confidence_points, 15),
            "calibration": component("calibration", calibration_status, calibration_points, 10),
            "bonuses": {
                "applied": ", ".join(bonuses) if bonuses else "none",
                "points": round(bonus_total, 1),
                "max": 10,
            },
        },
    )
