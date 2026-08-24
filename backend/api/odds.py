"""Odds endpoints: browse stored live games; trigger a refresh."""

from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from config import settings
from models import Game, GameOdds
from services.cache import StaleAwareCache
from services.pipeline import collect_and_store, collect_scores, odds_cache

router = APIRouter()

STALE_THRESHOLD = timedelta(hours=2)


def _latest_odds_per_side(db: Session, game: Game) -> list[dict[str, Any]]:
    rows = (
        db.query(GameOdds)
        .filter(GameOdds.game_id == game.id)
        .order_by(GameOdds.timestamp.desc(), GameOdds.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "sportsbook": r.sportsbook,
            "outcome_name": r.outcome_name,
            "market_type": r.market_type,
            "odds_american": r.odds_american,
            "odds_decimal": r.odds_decimal,
            "implied_probability": r.implied_probability,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in rows
    ]


@router.get("/odds/games")
def list_games(
    db: Annotated[Session, Depends(get_db)],
    sport: Annotated[str, Query(max_length=50)] = "americanfootball_nfl",
) -> dict[str, Any]:
    """Games for a sport with their latest odds, served from the local DB."""
    games = (
        db.query(Game)
        .filter(Game.sport == sport)
        .order_by(Game.game_time.desc())
        .limit(100)
        .all()
    )
    fetched_at = odds_cache.fetched_at(sport)
    stale = fetched_at is None or StaleAwareCache().is_stale(fetched_at)

    payload = [
        {
            "game_id": g.id,
            "sport": g.sport,
            "home_team": g.home_team.name if g.home_team else None,
            "away_team": g.away_team.name if g.away_team else None,
            "game_time": g.game_time.isoformat() if g.game_time else None,
            "status": g.status,
            "stale": stale,
            "fetched_at": fetched_at.isoformat() if fetched_at else None,
            "odds": _latest_odds_per_side(db, g),
        }
        for g in games
    ]
    return {"sport": sport, "stale": stale, "games": payload}


@router.post("/odds/refresh")
async def refresh_odds(
    db: Annotated[Session, Depends(get_db)],
    sport: Annotated[str, Query(max_length=50)] = "americanfootball_nfl",
) -> dict[str, Any]:
    """Fetch fresh odds from TheOddsAPI and persist them."""
    if not settings.theoddsapi_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "No TheOddsAPI key configured. "
                + "Set BETSIM_THEODDSAPI_API_KEY (see .env.example)."
            ),
        )
    try:
        report = await collect_and_store(db, sport)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Odds collection failed: {exc}") from exc

    return {
        "sport": report.sport,
        "games_stored": report.games_stored,
        "odds_stored": report.odds_stored,
        "odds_skipped": report.odds_skipped,
        "refreshed_at": datetime.now().isoformat(),
    }


@router.post("/odds/scores")
async def refresh_scores(
    db: Annotated[Session, Depends(get_db)],
    sport: Annotated[str, Query(max_length=50)] = "americanfootball_nfl",
    days_from: Annotated[int, Query(ge=1, le=3)] = 3,
) -> dict[str, Any]:
    """Fetch finished-game results, finalize stored games, auto-run backtests."""
    if not settings.theoddsapi_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "No TheOddsAPI key configured. "
                + "Set BETSIM_THEODDSAPI_API_KEY (see .env.example)."
            ),
        )
    try:
        report = await collect_scores(db, sport, days_from=days_from)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Score collection failed: {exc}") from exc

    return {
        "sport": report.sport,
        "games_finalized": report.games_finalized,
        "games_skipped": report.games_skipped,
        "backtests_created": report.backtests_created,
        "refreshed_at": datetime.now().isoformat(),
    }


