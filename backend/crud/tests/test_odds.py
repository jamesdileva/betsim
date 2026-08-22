import pytest

import crud.ml_models as model_crud
import crud.odds as odds_crud
from schemas.game import GameCreate, GameOddsCreate, TeamCreate
from schemas.ml_model import MlModelCreate, ModelPredictionCreate


@pytest.fixture()
def teams(db):
    home = odds_crud.save_team(db, TeamCreate(name="Chiefs", sport="football", league="NFL"))
    away = odds_crud.save_team(db, TeamCreate(name="Bills", sport="football", league="NFL"))
    return home.id, away.id


def test_save_and_get_game(db, teams) -> None:
    home_id, away_id = teams
    saved = odds_crud.save_game(
        db,
        GameCreate(id="game-1", sport="football", home_team_id=home_id, away_team_id=away_id),
    )
    assert isinstance(saved, GameCreate | object)  # returns GameRead pydantic model
    fetched = odds_crud.get_game(db, "game-1")
    assert fetched is not None
    assert fetched.status == "scheduled"
    assert fetched.home_team_id == home_id


def test_get_games_by_sport_filters(db, teams) -> None:
    odds_crud.save_game(db, GameCreate(id="nfl-1", sport="football"))
    odds_crud.save_game(db, GameCreate(id="nba-1", sport="basketball"))
    nfl = odds_crud.get_games_by_sport(db, "football")
    assert [g.id for g in nfl] == ["nfl-1"]


def test_save_and_query_odds(db) -> None:
    odds_crud.save_game(db, GameCreate(id="game-9", sport="football"))
    saved = odds_crud.save_game_odds(
        db,
        GameOddsCreate(
            game_id="game-9",
            sportsbook="draftkings",
            market_type="moneyline",
            outcome_name="home",
            odds_american=-110,
            odds_decimal=1.9091,
            implied_probability=0.5238,
        ),
    )
    assert saved.game_id == "game-9"
    rows = odds_crud.get_odds_for_game(db, "game-9", sportsbook="draftkings")
    assert len(rows) == 1
    assert rows[0].odds_american == -110


def test_ml_model_registry_round_trip(db) -> None:
    saved = model_crud.save_model(
        db, MlModelCreate(id="m1", name="stub", version="0.1.0")
    )
    assert saved.is_production is False

    prod = model_crud.save_model(
        db,
        MlModelCreate(id="m2", name="prod", version="1.0.0", is_production=True),
    )
    active = model_crud.get_active_model(db)
    assert active is not None
    assert active.id == prod.id

    assert model_crud.archive_model(db, "m2") is True
    assert model_crud.get_active_model(db) is None


def test_save_prediction_requires_existing_fk(db) -> None:
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        model_crud.save_prediction(
            db,
            ModelPredictionCreate(model_id="nope", game_id="nope", predicted_probability=0.6),
        )


def test_predictions_linked_to_model_and_game(db, teams) -> None:
    model_crud.save_model(db, MlModelCreate(id="m3"))
    odds_crud.save_game(db, GameCreate(id="g3", sport="football"))
    model_crud.save_prediction(
        db, ModelPredictionCreate(model_id="m3", game_id="g3", predicted_probability=0.62)
    )
    preds = model_crud.list_predictions_for_game(db, "g3", model_id="m3")
    assert len(preds) == 1
    assert preds[0].predicted_probability == pytest.approx(0.62)
