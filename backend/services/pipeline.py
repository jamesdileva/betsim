"""Collection pipeline: fetch -> normalize -> persist, with duplicate detection."""

import asyncio
from dataclasses import dataclass

from sqlalchemy.orm import Session

from config import settings
from crud.odds import get_game, get_odds_for_game, save_game, save_game_odds, save_team
from models import Team
from services import odds_api
from services.cache import StaleAwareCache
from services.collector import BaseCollector, TheOddsApiCollector
from services.normalizer import NormalizedGame, dedupe_odds, normalize_game


@dataclass
class CollectionReport:
    sport: str
    games_stored: int
    odds_stored: int
    odds_skipped: int


@dataclass
class ScoresReport:
    sport: str
    games_finalized: int
    games_skipped: int
    backtests_created: int


# shared in-memory cache; entries older than the TTL read as stale/absent
odds_cache = StaleAwareCache()


def _team_by_name(db: Session, name: str) -> Team | None:
    return db.query(Team).filter(Team.name == name).first()


def store_normalized_game(db: Session, normalized: NormalizedGame) -> tuple[int, int]:
    """Persist one normalized game. Returns (odds_stored, odds_skipped)."""
    if get_game(db, normalized.game.id) is None:
        # teams first so FKs resolve
        for team_model in (normalized.home_team, normalized.away_team):
            if team_model is not None and _team_by_name(db, team_model.name) is None:
                save_team(db, team_model)
        game_data = normalized.game
        if normalized.home_team is not None:
            home = _team_by_name(db, normalized.home_team.name)
            if home is not None:
                game_data = game_data.model_copy(update={"home_team_id": home.id})
        if normalized.away_team is not None:
            away = _team_by_name(db, normalized.away_team.name)
            if away is not None:
                game_data = game_data.model_copy(update={"away_team_id": away.id})
        save_game(db, game_data)

    existing = get_odds_for_game(db, normalized.game.id)
    stored = skipped = 0
    for row in normalized.odds:
        duplicate_in_db = any(
            e.sportsbook == row.sportsbook
            and e.market_type == row.market_type
            and e.outcome_name == row.outcome_name
            and e.timestamp == row.timestamp
            for e in existing
        )
        if duplicate_in_db:
            skipped += 1
            continue
        save_game_odds(db, row)
        stored += 1
    return stored, skipped


async def collect_and_store(
    db: Session, sport: str, collector: BaseCollector | None = None
) -> CollectionReport:
    """Fetch from the provider, normalize, and persist. Caches the raw payload."""
    if collector is None:
        if not settings.theoddsapi_api_key:
            raise odds_api.OddsApiError("No TheOddsAPI key configured")
        collector = TheOddsApiCollector(settings.theoddsapi_api_key)

    raw_games = await collector.fetch(sport)
    odds_cache.set(sport, raw_games)

    games_stored = 0
    odds_stored_total = 0
    odds_skipped_total = 0
    for raw_game in raw_games:
        normalized = normalize_game(raw_game)
        deduped = dedupe_odds(normalized.odds)
        odds_skipped_total += len(normalized.odds) - len(deduped)
        normalized.odds = deduped
        stored, skipped = store_normalized_game(db, normalized)
        odds_stored_total += stored
        odds_skipped_total += skipped
        games_stored += 1

    return CollectionReport(
        sport=sport,
        games_stored=games_stored,
        odds_stored=odds_stored_total,
        odds_skipped=odds_skipped_total,
    )


async def collect_scores(
    db: Session,
    sport: str,
    collector: BaseCollector | None = None,
    days_from: int = 3,
) -> ScoresReport:
    """Fetch finished-game results, finalize stored games, auto-run backtests.

    Score entries are matched to stored games by id; within a game the two
    score rows are matched to home/away by team name.
    """
    if collector is None:
        if not settings.theoddsapi_api_key:
            raise odds_api.OddsApiError("No TheOddsAPI key configured")
        collector = TheOddsApiCollector(settings.theoddsapi_api_key)

    raw_scores = await collector.fetch_scores(sport, days_from=days_from)

    from models import Game

    finalized = skipped = 0
    for entry in raw_scores:
        if not entry.get("completed"):
            continue
        game = db.query(Game).filter(Game.id == entry["id"]).first()
        if game is None:
            # Provider ids can vanish locally (fresh DB after a wipe/rebuild);
            # fall back to matching unfinished games by team names.
            home_name = str(entry.get("home_team") or "")
            away_name = str(entry.get("away_team") or "")
            candidates = (
                db.query(Game)
                .filter(
                    Game.sport == sport,
                    Game.status != "final",
                    Game.home_team_id.is_not(None),
                    Game.away_team_id.is_not(None),
                )
                .all()
            )
            for cand in candidates:
                if (
                    cand.home_team.name == home_name
                    and cand.away_team.name == away_name
                ):
                    game = cand
                    break
        if game is None or game.home_team is None or game.away_team is None:
            continue
        by_name = {
            str(s.get("name")): s.get("score")
            for s in entry.get("scores", [])
            if isinstance(s, dict)
        }
        home_score = by_name.get(game.home_team.name)
        away_score = by_name.get(game.away_team.name)
        if home_score is None or away_score is None:
            skipped += 1
            continue
        if game.status != "final":
            game.home_score = int(home_score)
            game.away_score = int(away_score)
            game.status = "final"
            db.commit()
            finalized += 1
        else:
            skipped += 1

    from ml.backtest import run_backtest

    backtests_created = run_backtest(db)

    return ScoresReport(
        sport=sport,
        games_finalized=finalized,
        games_skipped=skipped,
        backtests_created=backtests_created,
    )


class SchedulerService:
    """Periodically collects odds and results for configured sports."""

    def __init__(self, sports: list[str] | None = None, interval_minutes: int = 30) -> None:
        self.sports = sports or [
            s.strip() for s in settings.scheduler_sports.split(",") if s.strip()
        ]
        self.interval_minutes = interval_minutes
        self._task: asyncio.Task | None = None

    async def _loop(self) -> None:
        from database import SessionLocal

        while True:
            try:
                await asyncio.sleep(self.interval_minutes * 60)
                db = SessionLocal()
                try:
                    for sport in self.sports:
                        try:
                            await collect_and_store(db, sport)
                            await collect_scores(db, sport)
                        except Exception:  # noqa: S110 - logged via app log; keep looping
                            pass
                finally:
                    db.close()
            except asyncio.CancelledError:
                return

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None


