import pytest

import crud.backtest as backtest_crud
import crud.ml_models as model_crud
import crud.odds as odds_crud
import crud.portfolios as portfolio_crud
import crud.system_plays as system_plays_crud
from schemas.game import GameCreate
from schemas.ml_model import MlModelCreate, SystemPlayResultCreate
from schemas.portfolio import (
    BacktestResultCreate,
    ModelEvaluationCreate,
    PortfolioCreate,
    PortfolioItemCreate,
)


@pytest.fixture()
def game_and_model(db):
    odds_crud.save_game(db, GameCreate(id="g-1", sport="football"))
    model_crud.save_model(db, MlModelCreate(id="m-1", name="stub"))
    return "g-1", "m-1"


def test_save_calibration_result(db) -> None:
    saved = system_plays_crud.save_calibration_result(
        db,
        SystemPlayResultCreate(
            stated_probability=0.60,
            actual_win_rate=0.5987,
            calibration_error=0.0013,
            calibration_status="well_calibrated",
        ),
    )
    assert saved.id is not None
    listed = system_plays_crud.list_calibration_results(db)
    assert len(listed) == 1


def test_save_portfolio_with_items(db, game_and_model) -> None:
    _, model_id = game_and_model
    saved = portfolio_crud.save_portfolio(
        db,
        PortfolioCreate(
            total_risk=6.0,
            expected_roi=8.0,
            kelly_exposure=12.0,
            items=[
                PortfolioItemCreate(
                    confidence_level="high",
                    stake=200.0,
                    predicted_probability=0.74,
                ),
                PortfolioItemCreate(
                    confidence_level="medium",
                    stake=75.0,
                    predicted_probability=0.62,
                ),
            ],
        ),
    )
    assert saved.id is not None
    fetched = portfolio_crud.get_portfolio(db, saved.id)
    assert fetched is not None
    assert fetched.expected_roi == pytest.approx(8.0)
    assert fetched.model_id is None or fetched.model_id == model_id

    items = portfolio_crud.get_portfolio_items(db, saved.id)
    assert len(items) == 2
    assert {i.confidence_level for i in items} == {"high", "medium"}
    assert all(i.portfolio_id == saved.id for i in items)


def test_backtest_round_trip(db, game_and_model) -> None:
    game_id, model_id = game_and_model
    saved = backtest_crud.save_backtest_result(
        db,
        BacktestResultCreate(
            model_id=model_id,
            game_id=game_id,
            predicted_probability=0.62,
            actual_outcome=True,
            edge=0.08,
            roi=0.12,
        ),
    )
    assert saved.actual_outcome is True

    rows = backtest_crud.get_model_backtests(db, model_id)
    assert len(rows) == 1


def test_bulk_backtest_insert(db, game_and_model) -> None:
    game_id, model_id = game_and_model
    results = [
        BacktestResultCreate(
            model_id=model_id, game_id=game_id, predicted_probability=0.5 + i / 100
        )
        for i in range(50)
    ]
    count = backtest_crud.save_backtest_results(db, results)
    assert count == 50
    assert len(backtest_crud.get_model_backtests(db, model_id)) == 50


def test_model_evaluation_round_trip(db, game_and_model) -> None:
    _, model_id = game_and_model
    saved = portfolio_crud.save_model_evaluation(
        db,
        ModelEvaluationCreate(model_id=model_id, accuracy=0.71, brier_score=0.18),
    )
    assert saved.accuracy == pytest.approx(0.71)
    rows = portfolio_crud.list_evaluations_for_model(db, model_id)
    assert len(rows) == 1
