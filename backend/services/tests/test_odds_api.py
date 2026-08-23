import httpx
import pytest

from services import odds_api


class TestParseOddsResponse:
    def test_valid_payload_passes(self, provider_payload: list[dict]) -> None:
        assert odds_api.parse_odds_response(provider_payload) == provider_payload

    def test_non_list_rejected(self) -> None:
        with pytest.raises(odds_api.OddsApiError):
            odds_api.parse_odds_response({"error": "x"})

    def test_missing_fields_rejected(self) -> None:
        with pytest.raises(odds_api.OddsApiError):
            odds_api.parse_odds_response([{"id": "g1"}])

    def test_bookmakers_must_be_list(self) -> None:
        bad = [
            {"id": "g1", "sport_key": "nfl", "home_team": "A", "away_team": "B", "bookmakers": {}}
        ]
        with pytest.raises(odds_api.OddsApiError):
            odds_api.parse_odds_response(bad)


class TestFetchOdds:
    @pytest.mark.anyio
    async def test_success_parses_json(self, provider_payload: list[dict]) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            assert "apiKey=test-key" in url
            assert "/sports/americanfootball_nfl/odds/" in url
            assert "markets=h2h,spreads,totals" in url
            return httpx.Response(200, json=provider_payload)

        transport = httpx.MockTransport(handler)
        result = await odds_api.fetch_odds(
            "americanfootball_nfl", api_key="test-key", transport=transport
        )
        assert result == provider_payload

    @pytest.mark.anyio
    async def test_retries_then_succeeds(self, provider_payload: list[dict]) -> None:
        calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] < 3:
                return httpx.Response(500)
            return httpx.Response(200, json=provider_payload)

        result = await odds_api.fetch_odds(
            "americanfootball_nfl",
            api_key="test-key",
            transport=httpx.MockTransport(handler),
            backoff_seconds=0.0,
        )
        assert calls["n"] == 3
        assert result == provider_payload

    @pytest.mark.anyio
    async def test_gives_up_after_max_retries(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        with pytest.raises(odds_api.OddsApiError, match="after 2 attempts"):
            await odds_api.fetch_odds(
                "nfl",
                api_key="k",
                transport=httpx.MockTransport(handler),
                max_retries=2,
                backoff_seconds=0.0,
            )


