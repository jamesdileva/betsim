"""TheOddsAPI v4 client: fetches moneyline odds for a sport."""

from typing import Any

import httpx

from config import settings

BASE_URL = "https://api.the-odds-api.com/v4"


class OddsApiError(Exception):
    """Raised when TheOddsAPI request fails or returns invalid data."""


def build_odds_url(
    sport: str,
    api_key: str | None = None,
    markets: str = "h2h,spreads,totals",
) -> str:
    key = api_key if api_key is not None else settings.theoddsapi_api_key
    return (
        f"{BASE_URL}/sports/{sport}/odds/"
        f"?apiKey={key}&regions=us&markets={markets}&oddsFormat=american"
    )


def parse_odds_response(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate the shape of a TheOddsAPI response; raises OddsApiError on garbage."""
    if not isinstance(payload, list):
        raise OddsApiError("Expected a JSON array of games")
    for game in payload:
        for required in ("id", "sport_key", "home_team", "away_team", "bookmakers"):
            if required not in game:
                raise OddsApiError(f"Game payload missing field {required!r}")
        if not isinstance(game["bookmakers"], list):
            raise OddsApiError("'bookmakers' must be a list")
    return payload


async def fetch_odds(
    sport: str,
    *,
    api_key: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    """Fetch and validate odds with exponential-backoff retries."""
    url = build_odds_url(sport, api_key)
    last_error: Exception | None = None
    delay = backoff_seconds

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15, transport=transport) as client:
                response = await client.get(url)
                response.raise_for_status()
                return parse_odds_response(response.json())
        except (httpx.HTTPError, OddsApiError) as exc:
            last_error = exc
            if attempt < max_retries:
                import asyncio

                await asyncio.sleep(delay)
                delay *= 2

    raise OddsApiError(f"Failed to fetch odds after {max_retries} attempts: {last_error}")
