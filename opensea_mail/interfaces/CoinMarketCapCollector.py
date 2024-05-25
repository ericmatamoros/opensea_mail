
from typing import Optional

import pandas as pd
import requests
from loguru import logger
from requests import Response


class CoinMarketCapCollector:
    def __init__(self, api_key: str, ticker: str) -> None:
        self._headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }

        self._params = {
            'symbol': ticker,
            'convert': 'USD'
        }
        

    def get_price(self) -> Optional[Response]:

        # Define the API endpoint and headers
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

        # Make the GET request
        response = requests.get(url, headers=self._headers, params=self._params)
        data = response.json()
        if response.status_code == 200:
            price = data['data'][self._params['symbol']]['quote']['USD']['price']

        else:
            price = -1

        return price