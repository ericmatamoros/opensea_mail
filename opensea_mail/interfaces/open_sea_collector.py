"""OpenSea floor-price collector."""

from __future__ import annotations

from typing import Any

import requests


class OpenSeaCollector:
    """Fetch the floor price for one OpenSea collection."""

    API_URL = "https://api.opensea.io/api/v2/collections/{collection}/stats"

    def __init__(self, api_key: str, collection: str, timeout: float = 20.0) -> None:
        if not api_key:
            raise ValueError("OPENSEA_KEY is not configured")
        if not collection:
            raise ValueError("An OpenSea collection slug is required")

        self._headers = {"Accept": "application/json", "X-API-KEY": api_key}
        self._collection = collection
        self._timeout = timeout

    def get_fp(self) -> float:
        """Return the current floor price in ETH or raise a descriptive error."""
        try:
            response = requests.get(
                self.API_URL.format(collection=self._collection),
                headers=self._headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            floor_price = float(payload["total"]["floor_price"])
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Could not fetch the floor price for {self._collection}: {exc}"
            ) from exc

        if floor_price < 0:
            raise RuntimeError(
                f"OpenSea returned an invalid floor price for {self._collection}"
            )
        return floor_price
