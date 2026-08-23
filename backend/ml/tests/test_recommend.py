
from ml.recommend import calculate_intelligence_score


def test_score_matches_formula_with_all_bonuses() -> None:
    result = calculate_intelligence_score(
        predicted_prob=0.74,
        simulation_win_rate=0.81,
        ev=0.083,
        model_confidence=0.88,
        calibration_status="well_calibrated",
        risk_of_ruin=0.05,
    )
    import math

    expected = (
        0.74 * 25
        + 0.81 * 25
        + (1 / (1 + math.exp(-(0.083 / 0.10)))) * 25
        + 0.88 * 15
        + 10.0
        + 5.0  # strong ev? no — 0.083 < 0.10, so this bonus must NOT apply
    )
    # recompute properly: only +3 calibration and +2 sim-agreement bonuses apply
    expected = (
        0.74 * 25
        + 0.81 * 25
        + (1 / (1 + math.exp(-0.83))) * 25
        + 0.88 * 15
        + 10.0
        + 3.0
        + 2.0
    )
    assert result.score == round(min(expected, 100.0))
    assert result.stars == 4  # in [70, 85)
    assert result.risk_level == "Low"  # ruin 5%


def test_strong_ev_bonus_applies_above_ten_percent() -> None:
    base = calculate_intelligence_score(
        predicted_prob=0.6,
        simulation_win_rate=0.6,
        ev=0.10,
        model_confidence=0.5,
        calibration_status="miscalibrated",
    )
    with_bonus = calculate_intelligence_score(
        predicted_prob=0.6,
        simulation_win_rate=0.6,
        ev=0.11,
        model_confidence=0.5,
        calibration_status="miscalibrated",
    )
    assert with_bonus.score == base.score + 5
    applied = with_bonus.breakdown["bonuses"]["applied"]
    assert "strong_ev" in applied


def test_calibration_points_and_bonus() -> None:
    good = calculate_intelligence_score(
        predicted_prob=0.5,
        simulation_win_rate=0.5,
        ev=0.0,
        model_confidence=0.5,
        calibration_status="well_calibrated",
    )
    bad = calculate_intelligence_score(
        predicted_prob=0.5,
        simulation_win_rate=0.5,
        ev=0.0,
        model_confidence=0.5,
        calibration_status="overconfident",
    )
    # 10 vs 5 points + the +3 well-calibrated bonus
    assert good.score == bad.score + 8


def test_stars_thresholds() -> None:
    high = calculate_intelligence_score(
        predicted_prob=1.0,
        risk_of_ruin=None,
        simulation_win_rate=1.0,
        ev=0.2,
        model_confidence=1.0,
        calibration_status="well_calibrated",
    )
    assert high.score == 100  # clamped at the ceiling
    assert high.stars == 5

    # near-zero inputs, no bonuses -> deep in the one-star band
    low = calculate_intelligence_score(
        predicted_prob=0.05,
        simulation_win_rate=0.05,
        ev=-0.5,
        model_confidence=0.05,
        calibration_status="overconfident",
    )
    assert low.score < 40
    assert low.stars == 1


def test_risk_level_from_ruin_not_ev() -> None:
    result = calculate_intelligence_score(
        predicted_prob=0.9,
        simulation_win_rate=0.9,
        ev=0.30,  # doc's EV-based mapping would say High; ruin says Low
        model_confidence=0.9,
        calibration_status="well_calibrated",
        risk_of_ruin=0.03,
    )
    assert result.risk_level == "Low"


def test_inputs_clamped() -> None:
    result = calculate_intelligence_score(
        predicted_prob=2.0,
        simulation_win_rate=-1.0,
        ev=0.5,
        model_confidence=1.5,
        calibration_status="well_calibrated",
        risk_of_ruin=0.99,
    )
    # p->1 (25), sim->0 (0), ev sigmoid(5)*25 ~ 24.8, conf->1 (15),
    # calibration 10, bonuses +5 strong EV +3 calibration = 82.8 -> 83
    assert result.score == 83
    assert result.breakdown["probability"]["value"] == 1.0
    assert result.breakdown["simulation"]["value"] == 0.0
