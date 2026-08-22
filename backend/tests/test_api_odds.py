from datetime import datetime, timedelta

import pytest

from crud.odds import save_game_odds
from schemas.game import GameOddsCreate


def _seed_game(db) -> None:
    from crud.odds import save_game, save_team
    from schemas.game import GameCreate, TeamCreate

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


def test_list_games_empty_without_data(client) -> None:
    response = client.get("/api/odds/games?sport=basketball_nba")
    assert response.status_code == 200
    body = response.json()
    assert body["games"] == []
    assert body["stale"] is True  # never fetched


def test_list_games_returns_rows_with_staleness(db, client) -> None:
    _seed_game(db)
    fresh = datetime.now() - timedelta(minutes=5)

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
            timestamp=fresh,
        ),
    )

    # simulate a cache entry: fresh fetch -> stale=False for the sport
    from services.pipeline import odds_cache

    odds_cache.set("americanfootball_nfl", [{"raw": True}], now=datetime.now())
    response = client.get("/api/odds/games?sport=americanfootball_nfl")
    assert response.status_code == 200
    body = response.json()
    assert body["stale"] is False
    assert len(body["games"]) == 1
    game = body["games"][0]
    assert game["home_team"] == "Chiefs"
    assert game["odds"][0]["odds_american"] == -150
    implied = game["odds"][0]["implied_probability"]
    assert implied == pytest.approx(0.6)


def test_refresh_without_key_returns_503(client) -> None:
    # settings default to an empty key in tests
    response = client.post("/api/odds/refresh?sport=nfl")
    assert response.status_code == 503
    assert "BETSIM_THEODDSAPI_API_KEY" in response.json()["detail"]

