import pytest

from crud.ml_models import save_model, save_prediction
from crud.odds import save_game, save_team
from ml.backtest import evaluate_model, run_backtest
from schemas.game import GameCreate, TeamCreate
from schemas.ml_model import MlModelCreate, ModelPredictionCreate


def _seed(db) -> str:
    model = save_model(db, MlModelCreate(id="m1", name="stub"))
    home = save_team(db, TeamCreate(name="H", sport="s"))
    away = save_team(db, TeamCreate(name="A", sport="s"))
    save_game(
        db,
        GameCreate(
            id="g1",
            sport="s",
            home_team_id=home.id,
            away_team_id=away.id,
            home_score=28,
            away_score=14,
            status="final",
        ),
    )
    save_prediction(
        db,
        ModelPredictionCreate(model_id=model.id, game_id="g1", predicted_probability=0.7),
    )
    return model.id


def test_run_backtests_endpoint_populates_and_evaluates(db, client) -> None:
    model_id = _seed(db)

    response = client.post(f"/api/analytics/run-backtests?model_id={model_id}")
    assert response.status_code == 200
    assert response.json()["backtests_created"] == 1

    # second run: nothing new (idempotent)
    assert client.post("/api/analytics/run-backtests").json()["backtests_created"] == 0

    performance = client.get(f"/api/analytics/performance?model_id={model_id}")
    assert performance.status_code == 200
    body = performance.json()
    summary = body["summary"][0]
    assert summary["model_id"] == model_id
    assert summary["backtest_count"] == 1
    assert summary["accuracy"] == pytest.approx(1.0)

    evaluations = body["evaluations"].get(model_id, [])
    assert evaluations == []  # evaluate_model not called yet


def test_evaluate_via_endpoint_then_history(db, client) -> None:

    model_id = _seed(db)
    run_backtest(db, model_id=model_id)
    evaluation = evaluate_model(db, model_id)
    assert evaluation is not None

    performance = client.get(f"/api/analytics/performance?model_id={model_id}")
    history = performance.json()["evaluations"][model_id]
    assert len(history) == 1
    assert history[0]["brier_score"] is not None


def test_unknown_model_returns_404(client) -> None:
    assert client.post("/api/analytics/run-backtests?model_id=nope").status_code == 404
    assert client.get("/api/analytics/performance?model_id=nope").status_code == 404


def test_portfolio_history_empty(client) -> None:
    response = client.get("/api/analytics/portfolio-history")
    assert response.status_code == 200
    assert response.json()["portfolios"] == []
