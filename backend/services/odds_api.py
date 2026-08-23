"""TheOddsAPI v4 client: odds + finished-game scores, with retry/backoff."""

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


def build_scores_url(
    sport: str,
    api_key: str | None = None,
    days_from: int = 3,
) -> str:
    key = api_key if api_key is not None else settings.theoddsapi_api_key
    return f"{BASE_URL}/sports/{sport}/scores/?apiKey={key}&daysFrom={days_from}"


def parse_odds_response(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate the shape of a TheOddsAPI odds response; raises OddsApiError on garbage."""
    if not isinstance(payload, list):
        raise OddsApiError("Expected a JSON array of games")
    for game in payload:
        for required in ("id", "sport_key", "home_team", "away_team", "bookmakers"):
            if required not in game:
                raise OddsApiError(f"Game payload missing field {required!r}")
        if not isinstance(game["bookmakers"], list):
            raise OddsApiError("'bookmakers' must be a list")
    return payload


def parse_scores_response(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate the shape of a TheOddsAPI scores response."""
    if not isinstance(payload, list):
        raise OddsApiError("Expected a JSON array of score entries")
    for entry in payload:
        for required in ("id", "completed", "scores"):
            if required not in entry:
                raise OddsApiError(f"Score payload missing field {required!r}")
    return payload


async def _fetch_with_retries(
    url: str,
    *,
    parse: Any,
    transport: httpx.AsyncBaseTransport | None = None,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    delay = backoff_seconds

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15, transport=transport) as client:
                response = await client.get(url)
                response.raise_for_status()
                return parse(response.json())
        except (httpx.HTTPError, OddsApiError) as exc:
            last_error = exc
            if attempt < max_retries:
                import asyncio

                await asyncio.sleep(delay)
                delay *= 2

    raise OddsApiError(f"Failed to fetch after {max_retries} attempts: {last_error}")


async def fetch_odds(
    sport: str,
    *,
    api_key: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    """Fetch and validate odds with exponential-backoff retries."""
    return await _fetch_with_retries(
        build_odds_url(sport, api_key),
        parse=parse_odds_response,
        transport=transport,
        max_retries=max_retries,
        backoff_seconds=backoff_seconds,
    )


async def fetch_scores(
    sport: str,
    *,
    api_key: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
    days_from: int = 3,
) -> list[dict[str, Any]]:
    """Fetch game results (final scores) with exponential-backoff retries."""
    return await _fetch_with_retries(
        build_scores_url(sport, api_key, days_from),
        parse=parse_scores_response,
        transport=transport,
        max_retries=max_retries,
        backoff_seconds=backoff_seconds,
    )
