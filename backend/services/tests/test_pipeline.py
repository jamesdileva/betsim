"""Collection pipeline tests: store + duplicate skip across runs."""

import httpx
import pytest

from crud.odds import get_odds_for_game
from services import odds_api
from services.collector import TheOddsApiCollector
from services.pipeline import collect_and_store, collect_scores


@pytest.mark.anyio()
async def test_collect_without_key_raises_cleanly(db) -> None:
    with pytest.raises(odds_api.OddsApiError, match="No TheOddsAPI key"):
        await collect_scores(db, "nfl", collector=None)


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


@pytest.mark.anyio()
async def test_collect_scores_finalizes_game_and_runs_backtests(db, provider_payload) -> None:
    from crud.ml_models import save_model, save_prediction
    from crud.odds import get_game, save_game, save_team
    from models import BacktestResult
    from schemas.game import GameCreate, TeamCreate
    from schemas.ml_model import MlModelCreate, ModelPredictionCreate

    home = save_team(db, TeamCreate(name="Kansas City Chiefs", sport="americanfootball_nfl"))
    away = save_team(db, TeamCreate(name="Buffalo Bills", sport="americanfootball_nfl"))
    save_game(
        db,
        GameCreate(
            id="game-abc-123",
            sport="americanfootball_nfl",
            home_team_id=home.id,
            away_team_id=away.id,
            status="scheduled",
        ),
    )
    model = save_model(db, MlModelCreate(id="m1", name="stub"))
    save_prediction(
        db,
        ModelPredictionCreate(model_id=model.id, game_id="game-abc-123", predicted_probability=0.7),
    )

    scores_payload = [
        {
            "id": "game-abc-123",
            "completed": True,
            "home_team": "Kansas City Chiefs",
            "away_team": "Buffalo Bills",
            "scores": [
                {"name": "Kansas City Chiefs", "score": 31},
                {"name": "Buffalo Bills", "score": 20},
            ],
        },
        {
            # unknown to our DB: skipped silently
            "id": "unknown-game",
            "completed": True,
            "scores": [{"name": "X", "score": 1}],
        },
    ]
    collector = TheOddsApiCollector(
        api_key="test-key",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=scores_payload)
        ),
    )
    report = await collect_scores(db, "americanfootball_nfl", collector=collector)

    assert report.games_finalized == 1
    assert report.backtests_created == 1

    game = get_game(db, "game-abc-123")
    assert game.status == "final"
    assert game.home_score == 31
    assert game.away_score == 20

    rows = db.query(BacktestResult).all()
    assert len(rows) == 1
    assert rows[0].actual_outcome is True  # home won, prediction was 0.7


@pytest.mark.anyio
async def test_collect_scores_idempotent(db) -> None:
    """Already-final games are skipped; backtests don't duplicate."""
    from crud.odds import save_game, save_team
    from schemas.game import GameCreate, TeamCreate

    home = save_team(db, TeamCreate(name="A", sport="s"))
    away = save_team(db, TeamCreate(name="B", sport="s"))
    save_game(
        db,
        GameCreate(
            id="g-final",
            sport="s",
            home_team_id=home.id,
            away_team_id=away.id,
            status="final",
            home_score=10,
            away_score=7,
        ),
    )
    payload = [
        {
            "id": "g-final",
            "completed": True,
            "scores": [{"name": "A", "score": 10}, {"name": "B", "score": 7}],
        }
    ]
    collector = TheOddsApiCollector(
        api_key="k",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload)),
    )
    report = await collect_scores(db, "s", collector=collector)
    assert report.games_finalized == 0
    assert report.games_skipped == 1


def test_scheduler_sports_come_from_settings() -> None:
    from services.pipeline import SchedulerService

    service = SchedulerService()
    assert "americanfootball_nfl" in service.sports
    assert "mma_mixed_martial_arts" in service.sports
    custom = SchedulerService(sports=["soccer_epl"])
    assert custom.sports == ["soccer_epl"]
