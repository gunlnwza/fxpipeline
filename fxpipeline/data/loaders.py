import os
import logging
import requests
from abc import ABC, abstractmethod
from io import StringIO

import pandas as pd
from polygon import RESTClient

from core import ForexPriceRequest, ForexPrice

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ForexPriceLoader(ABC):
    def __init__(self, path: str, api_key: str):
        self.path = path
        self.api_key = api_key

    @abstractmethod
    def download(req: ForexPriceRequest, /) -> ForexPrice:
        pass

    def save(self, data: ForexPrice):  # TODO: delegate to dedicated database store
        os.makedirs(self.path, exist_ok=True)
        filename = f"{self.path}/{data.req.pair}.csv"
        data.df.to_csv(filename)
        logger.info(f"Save data to '{filename}'")

    def load(self, req: ForexPriceRequest) -> ForexPrice:
        filename = f"{self.path}/{req.pair}.csv"
        df = pd.read_csv(filename, index_col="timestamp", parse_dates=True)
        return ForexPrice(df, req)


class PolygonForex(ForexPriceLoader):
    def __init__(self, path, api_key):
        super().__init__(path, api_key)

    def download(self, req: ForexPriceRequest) -> ForexPrice:
        # download
        aggs = []
        client = RESTClient(self.api_key)
        for a in client.list_aggs(
            f"C:{req.pair}", 1, "day", req.start, req.end,
            adjusted="true", sort="asc"
        ):
            aggs.append(a)
        if not aggs:
            return None

        # clean
        df = pd.DataFrame(aggs)
        df.index = pd.to_datetime(df["timestamp"], unit="ms")
        for name in ("timestamp", "transactions", "otc"):
            df.drop(name, axis=1, inplace=True)

        return ForexPrice(df, req)


class AlphaVantageForex(ForexPriceLoader):
    def __init__(self, path, api_key):
        super().__init__(path, api_key)

    def download(self, req: ForexPriceRequest, full=False):
        """
        download price from Alpha Vantage
        return df on success, None on error

        Parameters
        [REQUIRED] `apikey`:
        [REQUIRED] `from_symbol`:
        [REQUIRED] `to_symbol`:
        [REQUIRED] `function`: FX_INTRADAY, FX_DAILY, FX_WEEKLY, FX_MONTHLY

        [REQUIRED if FX_INTRADAY] `interval`: 1min, 5min, 15min, 30min, 60min

        [OPTIONAL] `datatype`: default=json, csv
        [OPTIONAL if FX_INTRADAY, FX_DAILY] `outputsize`: default=compact, full

        NOTE: 4H is not supported by the API
        """
        params = {
            "apikey": self.api_key,
            "from_symbol": req.pair.base,
            "to_symbol": req.pair.quote,
            "function": "FX_DAILY",
            "datatype": "csv",
            "outputsize": "full" if full else "compact"
        }

        res = requests.get("https://www.alphavantage.co/query", params, timeout=10)
        if not res.ok:
            raise requests.exceptions.HTTPError(f"HTTP {res.status_code} — cannot download {req}")

        content_type = res.headers.get("Content-Type", "")
        if content_type and "json" in content_type.lower():
            msg = res.json()
            raise APIError(f"Asked for csv, but got json, likely an error message: {msg}")

        df = pd.read_csv(StringIO(res.text), index_col="timestamp", parse_dates=True)
        df = df.sort_index()
        return ForexPrice(df, req)


class YahooForex(ForexPriceLoader):
    def __init__(self, path):
        super().__init__(None, path)
