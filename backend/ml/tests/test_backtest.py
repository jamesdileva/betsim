from datetime import datetime

import pytest

from crud.ml_models import save_model, save_prediction
from crud.odds import save_game, save_team
from ml.backtest import evaluate_model, run_backtest
from schemas.game import GameCreate, TeamCreate
from schemas.ml_model import MlModelCreate, ModelPredictionCreate

# (game_id, home, away, home_score, away_score, predicted_prob, fair_odds)
PREDICTIONS = [
    ("g1", "A", "B", 30, 10, 0.7, 2.0),   # home win predicted 70% -> correct
    ("g2", "C", "D", 10, 24, 0.6, 2.0),   # home loss predicted 60% -> wrong
    ("g3", "E", "F", 21, 20, 0.4, None),  # home win, no fair odds stored
]


@pytest.fixture()
def seeded(db):
    model = save_model(db, MlModelCreate(id="m1", name="stub"))
    for game_id, home, away, hs, as_, prob, fair in PREDICTIONS:
        home_team = save_team(db, TeamCreate(name=home, sport="s"))
        away_team = save_team(db, TeamCreate(name=away, sport="s"))
        save_game(
            db,
            GameCreate(
                id=game_id,
                sport="s",
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_score=hs,
                away_score=as_,
                status="final",
            ),
        )
        save_prediction(
            db,
            ModelPredictionCreate(
                model_id=model.id,
                game_id=game_id,
                predicted_probability=prob,
                fair_odds_decimal=fair,
            ),
        )
    return model.id


def _backtest_rows(db):
    from models import BacktestResult

    return {r.game_id: r for r in db.query(BacktestResult).all()}


def test_run_backtest_matches_outcomes(db, seeded) -> None:
    created = run_backtest(db, model_id=seeded)
    assert created == 3
    rows = _backtest_rows(db)
    assert rows["g1"].actual_outcome is True   # home won
    assert rows["g2"].actual_outcome is False  # home lost
    assert rows["g3"].actual_outcome is True


def test_run_backtest_is_idempotent(db, seeded) -> None:
    assert run_backtest(db, model_id=seeded) == 3
    assert run_backtest(db, model_id=seeded) == 0


def test_edge_and_kelly_sized_roi(db, seeded) -> None:
    from simulation.kelly import kelly_criterion

    run_backtest(db, model_id=seeded)
    rows = _backtest_rows(db)

    # g1: p=0.7 at fair 2.0 -> edge = 0.7*2-1 = 0.4; win -> roi = kelly stake * (dec-1)
    assert rows["g1"].edge == pytest.approx(0.4)
    assert rows["g1"].roi == pytest.approx(kelly_criterion(2.0, 0.7))

    # g2: loss -> roi = -kelly stake
    assert rows["g2"].roi == pytest.approx(-kelly_criterion(2.0, 0.6))
    assert rows["g2"].edge == pytest.approx(0.6 * 2.0 - 1)

    # g3: no fair odds stored -> implied decimal = 1/0.4 -> edge = 0.4*2.5-1 = 0
    assert rows["g3"].edge == pytest.approx(0.0)


def test_evaluate_model_metrics_exact(db, seeded) -> None:
    run_backtest(db, model_id=seeded)
    evaluation = evaluate_model(db, seeded)
    assert evaluation is not None
    assert isinstance(evaluation.evaluated_at, datetime)

    # probs [0.7, 0.6, 0.4]; outcomes [T, F, T]
    # picks (home if p>=0.5): T, T, F -> only g1 correct => accuracy 1/3
    expected_brier = ((0.7 - 1) ** 2 + (0.6 - 0) ** 2 + (0.4 - 1) ** 2) / 3
    assert evaluation.accuracy == pytest.approx(1 / 3)
    assert evaluation.brier_score == pytest.approx(expected_brier)
    mean_p = (0.7 + 0.6 + 0.4) / 3
    assert evaluation.calibration_error == pytest.approx(abs(mean_p - 2 / 3))


def test_evaluate_model_without_results_returns_none(db, seeded) -> None:
    assert evaluate_model(db, seeded) is None
