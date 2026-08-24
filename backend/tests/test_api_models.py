import pytest

from crud.ml_models import save_model
from crud.odds import save_game, save_game_odds, save_team
from schemas.game import GameCreate, GameOddsCreate, TeamCreate
from schemas.ml_model import MlModelCreate


def _seed_game_with_odds(db) -> str:
    home = save_team(db, TeamCreate(name="Chiefs", sport="americanfootball_nfl"))
    away = save_team(db, TeamCreate(name="Bills", sport="americanfootball_nfl"))
    save_game(
        db,
        GameCreate(
            id="g-1",
            sport="americanfootball_nfl",
            home_team_id=home.id,
            away_team_id=away.id,
        ),
    )
    save_game_odds(
        db,
        GameOddsCreate(
            game_id="g-1",
            sportsbook="draftkings",
            market_type="moneyline",
            outcome_name="Chiefs",
            odds_american=-150,
            odds_decimal=1.6,
            implied_probability=0.6,
        ),
    )
    return "g-1"


def test_predict_user_input_returns_probability_and_factors(db, client) -> None:
    game_id = _seed_game_with_odds(db)
    response = client.post(
        "/api/models/predict",
        json={
            "source": "user_input",
            "win_probability": 0.62,
            "game_id": game_id,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["probability"] == pytest.approx(0.62)
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["fair_odds_decimal"] == pytest.approx(1 / 0.62, rel=1e-4)
    assert body["ev_vs_market"] is not None
    assert len(body["top_factors"]) <= 5
    # features extracted from the stored game (odds-derived present)
    assert body["features_used"] > 0


def test_predict_persists_when_model_registered(db, client) -> None:
    game_id = _seed_game_with_odds(db)
    save_model(db, MlModelCreate(id="m1", name="stub"))

    response = client.post(
        "/api/models/predict",
        json={
            "source": "user_input",
            "win_probability": 0.55,
            "confidence": 0.8,
            "game_id": game_id,
            "model_id": "m1",
        },
    )
    assert response.status_code == 200

    from crud.ml_models import list_predictions_for_game

    rows = list_predictions_for_game(db, game_id, model_id="m1")
    assert len(rows) == 1
    assert rows[0].predicted_probability == pytest.approx(0.55)


def test_predict_user_input_without_probability_422(client) -> None:
    response = client.post("/api/models/predict", json={"source": "user_input"})
    assert response.status_code == 422


def test_predict_unknown_source_422(client) -> None:
    response = client.post("/api/models/predict", json={"source": "gpt"})
    assert response.status_code == 422


def test_predict_unknown_game_404(client) -> None:
    response = client.post(
        "/api/models/predict",
        json={"source": "stub", "game_id": "missing"},
    )
    assert response.status_code == 404


def test_model_id_without_game_422(db, client) -> None:
    save_model(db, MlModelCreate(id="m2"))
    response = client.post(
        "/api/models/predict",
        json={"source": "stub", "win_probability": 0.5, "model_id": "m2"},
    )
    assert response.status_code == 422


def test_predict_away_side_converts_to_home_convention(db, client) -> None:
    """A 40% AWAY claim is a 60% HOME claim - storing it raw inverts the pick."""
    game_id = _seed_game_with_odds(db)
    save_model(db, MlModelCreate(id="m9"))

    response = client.post(
        "/api/models/predict",
        json={
            "source": "user_input",
            "win_probability": 0.40,
            "side": "away",
            "game_id": game_id,
            "model_id": "m9",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["side"] == "away"
    assert body["probability"] == pytest.approx(0.60)  # stored as home prob
    assert body["side_probability"] == pytest.approx(0.40)

    from crud.ml_models import list_predictions_for_game

    rows = list_predictions_for_game(db, game_id, model_id="m9")
    assert rows[-1].predicted_probability == pytest.approx(0.60)


def test_predict_invalid_side_422(client) -> None:
    response = client.post(
        "/api/models/predict",
        json={"source": "stub", "win_probability": 0.5, "side": "pitcher"},
    )
    assert response.status_code == 422


def test_models_list_round_trip(db, client) -> None:
    save_model(db, MlModelCreate(id="m1", name="prod", version="1.0", is_production=True))
    save_model(db, MlModelCreate(id="m2", name="archived", is_archived=True))

    listed = client.get("/api/models/list")
    ids = {m["id"] for m in listed.json()["models"]}
    assert ids == {"m1"}  # archived excluded by default

    listed_all = client.get("/api/models/list?include_archived=true")
    assert {m["id"] for m in listed_all.json()["models"]} == {"m1", "m2"}
