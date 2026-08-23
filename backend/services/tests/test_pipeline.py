"""Collection pipeline tests: store + duplicate skip across runs."""

import httpx
import pytest

from crud.odds import get_odds_for_game
from services import odds_api
from services.collector import TheOddsApiCollector
from services.pipeline import collect_and_store


@pytest.mark.anyio()
async def test_collect_and_store_persists_and_dedupes(db, provider_payload: list[dict]) -> None:
    collector = TheOddsApiCollector(
        api_key="test-key",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=provider_payload)),
    )

    first = await collect_and_store(db, "americanfootball_nfl", collector=collector)
    assert first.games_stored == 1
    assert first.odds_stored == 4
    assert first.odds_skipped == 0

    # second identical run must not create new rows (same timestamps)
    second = await collect_and_store(db, "americanfootball_nfl", collector=collector)
    assert second.games_stored == 1  # upsert path, no duplicate game
    assert second.odds_stored == 0
    assert second.odds_skipped == 4

    rows = get_odds_for_game(db, "game-abc-123")
    assert len(rows) == 4


@pytest.mark.anyio()
async def test_line_movement_creates_new_snapshot(db, provider_payload: list[dict]) -> None:
    collector = TheOddsApiCollector(
        api_key="test-key",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=provider_payload)),
    )
    await collect_and_store(db, "americanfootball_nfl", collector=collector)

    # move the line: same book, newer timestamp, different price
    updated = [{**provider_payload[0]}]
    updated[0] = {**updated[0]}
    updated[0]["bookmakers"] = [
        {
            **updated[0]["bookmakers"][0],
            "last_update": "2026-08-22T13:00:00Z",
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Kansas City Chiefs", "price": -135},
                        {"name": "Buffalo Bills", "price": 115},
                    ],
                }
            ],
        }
    ]
    moving = TheOddsApiCollector(
        api_key="test-key",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=updated)),
    )
    report = await collect_and_store(db, "americanfootball_nfl", collector=moving)
    assert report.odds_stored == 2

    rows = get_odds_for_game(db, "game-abc-123")
    assert len(rows) == 6  # original 4 + moved 2


def test_collect_without_key_raises_cleanly(db) -> None:
    with pytest.raises(odds_api.OddsApiError, match="No TheOddsAPI key"):
        # event loop provided by anyio marker would be needed; run directly
        import asyncio

        asyncio.run(collect_and_store(db, "nfl", collector=None))


def test_scheduler_sports_come_from_settings() -> None:
    from services.pipeline import SchedulerService

    service = SchedulerService()
    assert "americanfootball_nfl" in service.sports
    assert "mma_mixed_martial_arts" in service.sports
    custom = SchedulerService(sports=["soccer_epl"])
    assert custom.sports == ["soccer_epl"]
