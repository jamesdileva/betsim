from datetime import datetime

import pytest

from crud.odds import save_game, save_game_odds, save_team
from ml.features.engineering import extract_features
from ml.features.schema import FEATURE_NAMES
from models import Game, GameOdds
from schemas.game import GameCreate, GameOddsCreate, TeamCreate


@pytest.fixture()
def game_with_odds(db):
    home = save_team(db, TeamCreate(name="Chiefs", sport="football"))
    away = save_team(db, TeamCreate(name="Bills", sport="football"))
    save_game(
        db,
        GameCreate(
            id="g1", sport="americanfootball_nfl",
            home_team_id=home.id, away_team_id=away.id,
        ),
    )
    fetched_at = datetime(2026, 8, 22, 12, 0)
    for book, price in (("draftkings", -150), ("fanduel", -140)):
        save_game_odds(
            db,
            GameOddsCreate(
                game_id="g1",
                sportsbook=book,
                market_type="moneyline",
                outcome_name="Chiefs",
                odds_american=price,
                timestamp=fetched_at,
            ),
        )
    for book, price in (("draftkings", 130), ("fanduel", 120)):
        save_game_odds(
            db,
            GameOddsCreate(
                game_id="g1",
                sportsbook=book,
                market_type="moneyline",
                outcome_name="Bills",
                odds_american=price,
                timestamp=fetched_at,
            ),
        )
    return db.query(Game).filter_by(id="g1").one()


def _rows(db) -> list[GameOdds]:
    return db.query(GameOdds).filter_by(game_id="g1").all()


def test_feature_vector_has_all_schema_keys(db, game_with_odds) -> None:
    features = extract_features(game_with_odds, _rows(db))  # type: ignore[arg-type]
    assert set(features.keys()) == set(FEATURE_NAMES)
    assert len(FEATURE_NAMES) >= 30


def test_no_vig_math_exact(db, game_with_odds) -> None:
    features = extract_features(game_with_odds, _rows(db))  # type: ignore[arg-type]
    h = features["no_vig_home_prob"]
    a = features["no_vig_away_prob"]
    assert h is not None and a is not None
    assert h + a == pytest.approx(1.0)
    # -150 implied (0.60) vs +130 implied (~0.4348): home favored
    assert h > a
    assert features["vig_total"] == pytest.approx(
        features["home_implied_prob"] + features["away_implied_prob"] - 1.0
    )


def test_books_and_best_prices(db, game_with_odds) -> None:
    features = extract_features(game_with_odds, _rows(db))  # type: ignore[arg-type]
    assert features["books_count"] == 2
    assert features["best_home_price"] == -140  # higher than -150
    assert features["best_away_price"] == 130


def test_reserved_features_are_none_without_data(db, game_with_odds) -> None:
    features = extract_features(game_with_odds, _rows(db))  # type: ignore[arg-type]
    for name in ("home_win_rate_10", "home_injuries_count", "line_movement_hours"):
        assert features[name] is None


def test_empty_odds_still_returns_vector(db) -> None:
    home = save_team(db, TeamCreate(name="X", sport="s"))
    away = save_team(db, TeamCreate(name="Y", sport="s"))
    save_game(db, GameCreate(id="g2", sport="s", home_team_id=home.id, away_team_id=away.id))
    game = db.query(Game).filter_by(id="g2").one()
    features = extract_features(game, [])  # type: ignore[arg-type]
    assert set(features.keys()) == set(FEATURE_NAMES)
    assert all(v is None for v in features.values())


