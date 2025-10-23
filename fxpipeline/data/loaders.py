import os
from io import StringIO

from abc import ABC, abstractmethod

import logging
import warnings

import time
import datetime

import random
import numpy as np
import pandas as pd

import requests
import yfinance as yf
from urllib3.exceptions import MaxRetryError
from polygon import RESTClient

from forex_price import ForexPriceRequest, ForexPrice, make_forex_price_request
from currencies import make_pairs, CurrencyPair

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ForexPriceLoader(ABC):
    def __init__(self, path: str, api_key: str):
        self.path = path
        self.api_key = api_key

    @abstractmethod
    def download(req: ForexPriceRequest) -> ForexPrice:
        """connect to the internet and download, can raise APIError"""
        pass

    # TODO[database]: delegate to dedicated database store
    def save(self, data: ForexPrice):
        self._save(data.df, data.req.pair.ticker)

    # TODO[refactor]: lol, I just want easy interface,
    # but it's getting spaghetti now, but this one resemble pandas's though
    def _save(self, df: pd.DataFrame, ticker: str):
        os.makedirs(self.path, exist_ok=True)
        filename = f"{self.path}/{ticker}.csv"
        df.to_csv(filename)
        logger.info(f"Save data to '{filename}'")

    def load_every_row(self, ticker: str) -> pd.DataFrame:
        """
        load the entire time range of the ticker
        """
        filename = f"{self.path}/{ticker}.csv"
        return pd.read_csv(filename, index_col="timestamp", parse_dates=True)

    def load(self, req: ForexPriceRequest) -> ForexPrice:
        """
        load, and give only the slice of requested time range
        """
        df = self.load_every_row(req.pair.ticker)
        return ForexPrice(df[(req.start <= df.index) & (df.index <= req.end)], req)

    def have_in_cache(self, req: ForexPriceRequest) -> bool:
        filename = f"{self.path}/{req.pair}.csv"
        if os.path.exists(filename):
            return True
        return False

    def fetch(self, req: ForexPriceRequest) -> ForexPrice:
        """
        pretty much git fetch, download and cache
        """
        data = self.download(req)
        if data is None:
            logger.warning("data is None, meaning is has not been downloaded")
            return None

        # TODO[download]: subtract time range and only download the really needed newer portion
        if self.have_in_cache(req):
            old_df = self.load_every_row(req.pair.ticker)
            new_df = pd.concat([old_df, data.df], ignore_index=False)
            new_df = new_df[~new_df.index.duplicated(keep="last")]
        else:
            new_df = data.df
        self._save(new_df, req.pair.ticker)

        return data

    def fetch_with_retries(self, req: ForexPriceRequest, retries=5, max_retry_wait=30) -> bool:
        """
        attempting to fetch for several times
        """
        logger.info(f"Fetching {req.pair}...")
        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"Fetching {req.pair} (attempt {attempt})...")
                self.fetch(req)
                time.sleep(random.randint(1, 3))
                return True
            except MaxRetryError as e:
                logger.error(f"MaxRetryError: {e} ; retrying in {max_retry_wait:.1f}s...")
                if attempt < retries:
                    time.sleep(max_retry_wait)
        return False

    def fetch_all_pairs(self, currencies: list[str], days=1000):
        """
        fetch every combination of the given currencies
        """
        pairs = make_pairs(currencies)
        try:
            for pair in pairs:
                # TODO[inconsistency]: currently 'days' is not really doing much except for using with Polygon API
                req = make_forex_price_request(pair.ticker, days)
                if self.have_in_cache(req):  # TODO[data]: need to take into account if we have the requested time range:
                    logger.debug(f"We already have '{req}' ; Skipping")
                    continue
                if self.fetch_with_retries(req):
                    continue
                req.pair = req.pair.reverse()
                if self.fetch_with_retries(req):
                    continue
                logger.warning(f"No data available for '{req.pair}', perhaps too exotic")
        except APIError as e:
            logger.error(e)

    def fetch_pair(self, ticker: str, days=1000):
        self.fetch_all_pairs([ticker[:3], ticker[3:]], days)


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

    def download(self, req: ForexPriceRequest):
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
        # logger.debug(req.__repr__)
        business_day = np.busday_count(req.start.date(), req.end.date() + datetime.timedelta(1))
        download_full = business_day >= 100
        params = {
            "apikey": self.api_key,
            "from_symbol": req.pair.base,
            "to_symbol": req.pair.quote,
            "function": "FX_DAILY",
            "datatype": "csv",
            "outputsize": "full" if download_full else "compact"
        }

        res = requests.get("https://www.alphavantage.co/query", params, timeout=10)
        if not res.ok:
            logger.error(f"HTTP {res.status_code} — cannot download {req}")
            return None

        content_type = res.headers.get("Content-Type", "")
        if content_type and "json" in content_type.lower():
            msg = res.json()
            raise APIError(f"Alpha Vantage API error: {msg}")

        df = pd.read_csv(StringIO(res.text), index_col="timestamp", parse_dates=True)
        df = df.sort_index()
        return ForexPrice(df, req)


class YahooFinanceForex(ForexPriceLoader):
    def __init__(self, path):
        super().__init__(path, None)

    def _convert_to_yf_ticker(self, pair: CurrencyPair) -> str:
        if pair.base == "USD":
            return f"{pair.quote}=X"
        elif pair.quote == "USD":
            return f"{pair.base}=X"
        return f"{pair.ticker}=X"

    def download(self, req: ForexPriceRequest) -> ForexPrice:
        # download
        ticker = self._convert_to_yf_ticker(req.pair)
        warnings.filterwarnings("ignore")
        df = yf.download(ticker, req.start, req.end, progress=False)
        warnings.filterwarnings("default")

        # clean
        df.columns = df.columns.droplevel("Ticker")
        df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"}, inplace=True)
        df.index.name = "timestamp"

        return ForexPrice(df, req)
