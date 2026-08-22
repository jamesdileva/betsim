"""CRUD operations for teams, games, and odds."""

from sqlalchemy.orm import Session

from models import Game, GameOdds, Team
from schemas.game import (
    GameCreate,
    GameOddsCreate,
    GameOddsRead,
    GameRead,
    TeamCreate,
)


def save_team(db: Session, data: TeamCreate) -> Team:
    team = Team(**data.model_dump())
    db.add(team)
    try:
        db.commit()
        db.refresh(team)
    except Exception:
        db.rollback()
        raise
    return team


def save_game(db: Session, data: GameCreate) -> GameRead:
    game = Game(**data.model_dump())
    db.add(game)
    try:
        db.commit()
        db.refresh(game)
    except Exception:
        db.rollback()
        raise
    return GameRead.model_validate(game)


def get_game(db: Session, game_id: str) -> GameRead | None:
    game = db.get(Game, game_id)
    return GameRead.model_validate(game) if game else None


def get_games_by_sport(db: Session, sport: str) -> list[GameRead]:
    games = (
        db.query(Game)
        .filter(Game.sport == sport)
        .order_by(Game.game_time.desc())
        .all()
    )
    return [GameRead.model_validate(g) for g in games]


def save_game_odds(db: Session, data: GameOddsCreate) -> GameOddsRead:
    odds = GameOdds(**data.model_dump())
    db.add(odds)
    try:
        db.commit()
        db.refresh(odds)
    except Exception:
        db.rollback()
        raise
    return GameOddsRead.model_validate(odds)


def get_odds_for_game(
    db: Session, game_id: str, sportsbook: str | None = None
) -> list[GameOddsRead]:
    query = db.query(GameOdds).filter(GameOdds.game_id == game_id)
    if sportsbook is not None:
        query = query.filter(GameOdds.sportsbook == sportsbook)
    rows = query.order_by(GameOdds.timestamp.desc()).all()
    return [GameOddsRead.model_validate(r) for r in rows]
