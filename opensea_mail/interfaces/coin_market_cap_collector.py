"""CoinMarketCap price collector."""

from __future__ import annotations

from typing import Any

import requests


class CoinMarketCapCollector:
    """Fetch the USD price for one cryptocurrency ticker."""

    API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    def __init__(self, api_key: str, ticker: str, timeout: float = 20.0) -> None:
        if not api_key:
            raise ValueError("COINMARKETCAP_KEY is not configured")
        if not ticker:
            raise ValueError("A cryptocurrency ticker is required")

        self._headers = {
            "Accept": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }
        self._ticker = ticker.upper()
        self._timeout = timeout

    def get_price(self) -> float:
        """Return the current USD price or raise a descriptive error."""
        try:
            response = requests.get(
                self.API_URL,
                headers=self._headers,
                params={"symbol": self._ticker, "convert": "USD"},
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            price = float(payload["data"][self._ticker]["quote"]["USD"]["price"])
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Could not fetch the USD price for {self._ticker}: {exc}"
            ) from exc

        if price < 0:
            raise RuntimeError(
                f"CoinMarketCap returned an invalid price for {self._ticker}"
            )
        return price
