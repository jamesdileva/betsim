
from crud.ml_models import save_model, save_prediction
from crud.odds import save_game, save_team
from schemas.game import GameCreate, TeamCreate
from schemas.ml_model import MlModelCreate, ModelPredictionCreate


def _seed_predictions(db) -> str:
    save_model(db, MlModelCreate(id="m1", name="stub"))
    home = save_team(db, TeamCreate(name="H", sport="s"))
    away = save_team(db, TeamCreate(name="A", sport="s"))
    save_game(
        db,
        GameCreate(
            id="g1",
            sport="s",
            home_team_id=home.id,
            away_team_id=away.id,
            status="scheduled",
        ),
    )
    save_prediction(
        db,
        ModelPredictionCreate(
            model_id="m1",
            game_id="g1",
            predicted_probability=0.9,
            confidence=0.8,
            fair_odds_decimal=1.2,
        ),
    )
    return "m1"


def test_build_persists_and_returns_portfolio(db, client) -> None:
    model_id = _seed_predictions(db)

    response = client.post(f"/api/portfolio/build?bankroll=1000&model_id={model_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None

    latest = client.get("/api/portfolio/latest")
    assert latest.status_code == 200
    assert latest.json()["id"] == body["id"]

    history = client.get("/api/portfolio/history")
    portfolios = history.json()["portfolios"]
    assert len(portfolios) == 1
    assert portfolios[0]["items"] >= 1


def test_scored_preview_returns_scores(client, db) -> None:
    _seed_predictions(db)
    response = client.get("/api/portfolio/scored")
    assert response.status_code == 200
    rows = response.json()["predictions"]
    assert len(rows) == 1
    row = rows[0]
    for key in ("score", "stars", "risk_level", "band"):
        assert key in row


def test_build_unknown_model_404(client) -> None:
    response = client.post("/api/portfolio/build?bankroll=1000&model_id=nope")
    assert response.status_code == 404


def test_build_invalid_bankroll_422(client) -> None:
    response = client.post("/api/portfolio/build?bankroll=0")
    assert response.status_code == 422


def test_latest_empty_returns_null(client) -> None:
    response = client.get("/api/portfolio/latest")
    assert response.status_code == 200
    assert response.json() is None or response.json() == {}
