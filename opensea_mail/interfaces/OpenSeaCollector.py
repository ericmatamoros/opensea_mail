
from typing import Optional

import pandas as pd
import requests
from loguru import logger
from requests import Response


class OpenSeaCollector:
    def __init__(self, api_key: str, collection: str) -> None:
        self._headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key,
        }
        self._collection = collection
        

    def get_fp(self) -> Optional[Response]:
        # Construct the API endpoint URL

        # Define the API endpoint and headers
        url = f"https://api.opensea.io/api/v2/collections/{self._collection}/stats"

        # Make the GET request
        response = requests.get(url, headers=self._headers)
        data = response.json()
        if response.status_code == 200:
            fp = float(data['total']['floor_price'])

        else:
            fp = -1

        
        return fp