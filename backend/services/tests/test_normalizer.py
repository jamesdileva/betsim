import pytest

from schemas.game import GameOddsCreate
from services.normalizer import dedupe_odds, has_odds_snapshot, normalize_game


def _first_game(provider_payload: list[dict]) -> dict:
    return provider_payload[0]


class TestNormalizeGame:
    def test_maps_core_fields(self, provider_payload: list[dict]) -> None:
        normalized = normalize_game(_first_game(provider_payload))
        assert normalized.game.id == "game-abc-123"
        assert normalized.game.sport == "americanfootball_nfl"
        assert normalized.home_team is not None
        assert normalized.home_team.name == "Kansas City Chiefs"
        assert normalized.game.status == "scheduled"
        assert normalized.raw_json.startswith("{")

    def test_moneyline_rows_have_implied_prob(self, provider_payload: list[dict]) -> None:
        normalized = normalize_game(_first_game(provider_payload))
        # 2 books x 2 outcomes = 4 rows
        assert len(normalized.odds) == 4
        dk_home = next(
            r
            for r in normalized.odds
            if r.sportsbook == "draftkings" and r.outcome_name == "Kansas City Chiefs"
        )
        assert dk_home.odds_american == -150
        assert dk_home.odds_decimal == pytest.approx(1 + 100 / 150)
        assert dk_home.implied_probability == pytest.approx(150 / 250)

    def test_spreads_and_totals_markets_normalized(self, provider_payload: list[dict]) -> None:
        game = _first_game(provider_payload)
        game["bookmakers"][0]["markets"].extend(
            [
                {
                    "key": "spreads",
                    "outcomes": [
                        {"name": "Kansas City Chiefs -3.5", "price": -105},
                        {"name": "Buffalo Bills +3.5", "price": -115},
                    ],
                },
                {
                    "key": "totals",
                    "outcomes": [
                        {"name": "Over 47.5", "price": -110},
                        {"name": "Under 47.5", "price": -110},
                    ],
                },
            ]
        )
        normalized = normalize_game(game)
        by_type = {r.market_type for r in normalized.odds}
        assert by_type == {"moneyline", "spreads", "totals"}
        spread = next(
            r
            for r in normalized.odds
            if r.market_type == "spreads" and r.outcome_name == "Kansas City Chiefs -3.5"
        )
        assert spread.sportsbook == "draftkings"
        assert spread.implied_probability == pytest.approx(105 / 205)

    def test_invalid_prices_skipped(self, provider_payload: list[dict]) -> None:
        game = _first_game(provider_payload)
        game["bookmakers"][0]["markets"][0]["outcomes"].append({"name": "Bad", "price": "n/a"})
        normalized = normalize_game(game)
        assert not any(r.outcome_name == "Bad" for r in normalized.odds)


class TestDuplicateDetection:
    def test_same_snapshot_detected(self) -> None:
        ts = "2026-08-22T12:00:00+00:00"
        from datetime import datetime

        row = GameOddsCreate(
            game_id="g1",
            sportsbook="dk",
            market_type="moneyline",
            outcome_name="Home",
            odds_american=-110,
            timestamp=datetime.fromisoformat(ts),
        )
        assert has_odds_snapshot([row], row.model_copy()) is True

    def test_new_timestamp_is_not_duplicate(self) -> None:
        from datetime import datetime

        base = dict(
            game_id="g1",
            sportsbook="dk",
            market_type="moneyline",
            outcome_name="Home",
        )
        old = GameOddsCreate(**base, odds_american=-110, timestamp=datetime(2026, 8, 1))
        new = GameOddsCreate(**base, odds_american=-105, timestamp=datetime(2026, 8, 2))
        assert has_odds_snapshot([old], new) is False

    def test_dedupe_keeps_first_and_drops_repeats(self) -> None:
        from datetime import datetime

        base = dict(game_id="g1", sportsbook="dk", market_type="moneyline", outcome_name="H")
        rows = [
            GameOddsCreate(**base, odds_american=-110, timestamp=datetime(2026, 8, 1)),
            GameOddsCreate(**base, odds_american=-110, timestamp=datetime(2026, 8, 1)),
            GameOddsCreate(**base, odds_american=-108, timestamp=datetime(2026, 8, 1)),
        ]
        assert len(dedupe_odds(rows)) == 1

