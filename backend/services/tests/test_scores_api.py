import httpx
import pytest

from services import odds_api


class TestParseScoresResponse:
    def test_valid_payload_passes(self) -> None:
        payload = [
            {
                "id": "g1",
                "completed": True,
                "scores": [{"name": "A", "score": 24}, {"name": "B", "score": 17}],
            },
            {"id": "g2", "completed": False, "scores": []},
        ]
        assert odds_api.parse_scores_response(payload) == payload

    def test_non_list_rejected(self) -> None:
        with pytest.raises(odds_api.OddsApiError):
            odds_api.parse_scores_response({"error": "x"})

    def test_missing_fields_rejected(self) -> None:
        with pytest.raises(odds_api.OddsApiError):
            odds_api.parse_scores_response([{"id": "g1"}])


class TestFetchScores:
    @pytest.mark.anyio
    async def test_url_and_parse(self) -> None:
        payload = [{"id": "g1", "completed": True, "scores": []}]

        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            assert "/sports/americanfootball_nfl/scores/" in url
            assert "daysFrom=5" in url
            assert "apiKey=test-key" in url
            return httpx.Response(200, json=payload)

        result = await odds_api.fetch_scores(
            "americanfootball_nfl",
            api_key="test-key",
            transport=httpx.MockTransport(handler),
            days_from=5,
        )
        assert result == payload

    @pytest.mark.anyio
    async def test_retries_exhausted_raises(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        with pytest.raises(odds_api.OddsApiError):
            await odds_api.fetch_scores(
                "nfl",
                api_key="k",
                transport=httpx.MockTransport(handler),
                max_retries=2,
                backoff_seconds=0.0,
            )
