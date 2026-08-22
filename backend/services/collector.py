"""Collector interface + TheOddsAPI collector."""

from abc import ABC, abstractmethod
from typing import Any

import httpx

from services import odds_api


class BaseCollector(ABC):
    """A data provider that returns raw odds payloads for a sport."""

    @abstractmethod
    async def fetch(self, sport: str) -> list[dict[str, Any]]:
        """Fetch raw provider data. Returns a list of raw game dicts."""

    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier."""


class TheOddsApiCollector(BaseCollector):
    def __init__(
        self,
        api_key: str,
        transport: httpx.AsyncBaseTransport | None = None,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.transport = transport
        self.max_retries = max_retries

    def provider_name(self) -> str:
        return "the-odds-api"

    async def fetch(self, sport: str) -> list[dict[str, Any]]:
        return await odds_api.fetch_odds(
            sport,
            api_key=self.api_key,
            transport=self.transport,
            max_retries=self.max_retries,
        )
