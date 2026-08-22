"""Feature extraction: normalized game + odds rows -> model-ready vector."""

from datetime import datetime

from ml.features.schema import FEATURE_NAMES
from models import Game, GameOdds
from simulation.odds import OddsConversion


def _naive(ts: datetime | None) -> datetime | None:
    if ts is not None and ts.tzinfo is not None:
        return ts.replace(tzinfo=None)
    return ts


def _latest_for(rows: list[GameOdds], outcome_name: str | None) -> GameOdds | None:
    """Newest moneyline row for one side (by timestamp, then id)."""
    candidates = [
        r
        for r in rows
        if r.market_type == "moneyline"
        and outcome_name is not None
        and r.outcome_name == outcome_name
    ]
    return max(
        candidates,
        key=lambda r: (_naive(r.timestamp) or datetime.min, r.id),
        default=None,
    )


def _prices_for(rows: list[GameOdds], row: GameOdds | None) -> list[int]:
    if row is None:
        return []
    return [
        r.odds_american
        for r in rows
        if r.outcome_name == row.outcome_name and r.odds_american is not None
    ]


def extract_features(
    game: Game,
    odds_rows: list[GameOdds],
    *,
    now: datetime | None = None,
) -> dict[str, float | None]:
    """Build the feature vector defined in schema.FEATURES.

    Odds-derived and time features are computed when data allows; history,
    injury, and line-movement features are reserved (None) until their data
    sources exist.
    """
    now = now or datetime.now()
    features: dict[str, float | None] = {name: None for name in FEATURE_NAMES}

    if game.game_time:
        kickoff = _naive(game.game_time)
        assert kickoff is not None
        features["hours_until_game"] = max(0.0, (kickoff - now).total_seconds() / 3600.0)
        features["is_weekend_game"] = 1.0 if kickoff.weekday() >= 5 else 0.0
        features["hour_of_day"] = float(kickoff.hour)

    if not odds_rows:
        return features

    features["books_count"] = float(len({r.sportsbook for r in odds_rows}))
    home_row = _latest_for(odds_rows, game.home_team.name if game.home_team else None)
    away_row = _latest_for(odds_rows, game.away_team.name if game.away_team else None)

    for side, row in (("home", home_row), ("away", away_row)):
        prices = _prices_for(odds_rows, row)
        if not prices:
            continue
        best = max(prices)
        latest = float(row.odds_american) if row.odds_american is not None else float(best)
        features[f"{side}_odds_american"] = latest
        features[f"{side}_odds_decimal"] = OddsConversion.american_to_decimal(int(best))
        features[f"{side}_implied_prob"] = OddsConversion.american_to_implied_prob(int(best))
        features[f"best_{side}_price"] = float(best)
        if side == "home":
            features["price_spread_home"] = float(max(prices) - min(prices))

    h, a = features["home_implied_prob"], features["away_implied_prob"]
    if h is not None and a is not None and (h + a) > 0:
        total = h + a
        features["no_vig_home_prob"] = h / total
        features["no_vig_away_prob"] = a / total
        features["vig_total"] = total - 1.0

    return features
