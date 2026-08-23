"""Normalizer: provider payloads -> canonical teams/games/odds + raw audit rows."""

from datetime import datetime
from typing import Any

from schemas.game import GameCreate, GameOddsCreate, TeamCreate
from simulation.odds import OddsConversion


class NormalizedGame:
    """One provider game mapped to canonical create-models plus raw JSON."""

    def __init__(
        self,
        game: GameCreate,
        odds: list[GameOddsCreate],
        raw_json: str,
        home_team: TeamCreate | None,
        away_team: TeamCreate | None,
    ) -> None:
        self.game = game
        self.odds = odds
        self.raw_json = raw_json
        self.home_team = home_team
        self.away_team = away_team


def _parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO timestamp and normalize to naive UTC so that duplicate
    detection compares consistently with values round-tripped from SQLite."""
    if not value:
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(tz=None).replace(tzinfo=None)
    return parsed


SUPPORTED_MARKETS = ("h2h", "spreads", "totals")


def normalize_game(raw_game: dict[str, Any]) -> NormalizedGame:
    """Map one TheOddsAPI game dict to canonical models (h2h/spreads/totals)."""
    game_id = str(raw_game["id"])
    sport = str(raw_game.get("sport_key") or "unknown")
    commence = _parse_timestamp(raw_game.get("commence_time"))
    status = "scheduled" if commence is None or commence > datetime.now() else "live"

    home_name = str(raw_game.get("home_team") or "").strip()
    away_name = str(raw_game.get("away_team") or "").strip()

    home_team = TeamCreate(name=home_name, sport=sport) if home_name else None
    away_team = TeamCreate(name=away_name, sport=sport) if away_name else None

    game = GameCreate(
        id=game_id,
        sport=sport,
        league=raw_game.get("sport_title"),
        game_time=commence,
        status=status,
    )

    odds_rows: list[GameOddsCreate] = []
    for book in raw_game.get("bookmakers", []):
        sportsbook = str(book.get("key") or book.get("title") or "unknown")
        last_update = _parse_timestamp(book.get("last_update"))
        for market in book.get("markets", []):
            market_key = str(market.get("key") or "")
            if market_key not in SUPPORTED_MARKETS:
                continue
            market_type = "moneyline" if market_key == "h2h" else market_key
            for outcome in market.get("outcomes", []):
                american = outcome.get("price")
                if not isinstance(american, int):
                    continue
                try:
                    decimal = OddsConversion.american_to_decimal(american)
                    implied = OddsConversion.american_to_implied_prob(american)
                except ValueError:
                    continue
                odds_rows.append(
                    GameOddsCreate(
                        game_id=game_id,
                        sportsbook=sportsbook,
                        market_type=market_type,
                        outcome_name=str(outcome.get("name") or ""),
                        odds_american=american,
                        odds_decimal=decimal,
                        implied_probability=implied,
                        timestamp=last_update,
                    )
                )
    import json

    return NormalizedGame(
        game=game,
        odds=odds_rows,
        raw_json=json.dumps(raw_game),
        home_team=home_team,
        away_team=away_team,
    )


def has_odds_snapshot(
    existing: list[GameOddsCreate], candidate: GameOddsCreate
) -> bool:
    """Duplicate detection: same game + book + market + timestamp already seen."""
    for row in existing:
        if (
            row.sportsbook == candidate.sportsbook
            and row.market_type == candidate.market_type
            and row.outcome_name == candidate.outcome_name
            and row.timestamp == candidate.timestamp
        ):
            return True
    return False


def dedupe_odds(rows: list[GameOddsCreate]) -> list[GameOddsCreate]:
    unique: list[GameOddsCreate] = []
    for row in rows:
        if not has_odds_snapshot(unique, row):
            unique.append(row)
    return unique
