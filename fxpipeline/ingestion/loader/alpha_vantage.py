import logging
from io import StringIO
import requests
import time

import numpy as np
import pandas as pd

from ..base import ForexPriceLoader
from ..error import APIError, APIRateLimit, NotDownloadedError
from ...core import CurrencyPair, ForexPrices


logger = logging.getLogger(__name__)


class AlphaVantageForex(ForexPriceLoader):
    def __init__(self, api_key: str):
        super().__init__("alpha_vantage", api_key)

    @staticmethod
    def _should_download_full(start: pd.Timestamp, end: pd.Timestamp) -> bool:
        business_day = np.busday_count(start.date(), end.date() + pd.Timedelta(days=1))
        return business_day >= 100

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_index()
        df["volume"] = 0
        return df

    def download(
        self,
        pair: CurrencyPair,
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str = "1d",
    ) -> ForexPrices:
        """
        Download price from Alpha Vantage

        ### Parameters

        - Required
            - `apikey`
            - `from_symbol`
            - `to_symbol`
            - `function`: FX_INTRADAY, FX_DAILY, FX_WEEKLY, FX_MONTHLY
            - `interval` (If FX_INTRADAY): 1min, 5min, 15min, 30min, 60min
        - Optional
            - `datatype`: default=json, csv
            - `outputsize` (If FX_INTRADAY, FX_DAILY): default=compact, full

        NOTE: 4H is not supported by the API
        """
        logger.debug(f"Downloading {pair} with Alpha Vantage API")

        params = {
            "apikey": self.api_key,
            "from_symbol": pair.base,
            "to_symbol": pair.quote,
            "function": "FX_DAILY",
            "datatype": "csv",
            "outputsize": "full"
            if self._should_download_full(start, end)
            else "compact",
        }
        res = requests.get("https://www.alphavantage.co/query", params, timeout=10)
        if not res.ok:
            raise NotDownloadedError(
                f"Alpha Vantage: HTTP {res.status_code} — cannot download {pair}"
            )

        content_type = res.headers.get("Content-Type", "")
        if content_type and "json" in content_type.lower():
            msg = res.json()
            if "rate limit" in msg["Note"].lower():
                raise APIRateLimit(f"Alpha Vantage API rate limit: {msg}")
            raise APIError(f"Alpha Vantage API error: {msg}")

        df = pd.read_csv(StringIO(res.text), index_col="timestamp", parse_dates=True)
        df = self._clean(df)
        return ForexPrices(pair.copy(), self.name, df)
