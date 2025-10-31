import os
import logging
import time
import random
from abc import ABC, abstractmethod

import pandas as pd
from urllib3.exceptions import MaxRetryError

from ..core import make_pairs, ForexPriceRequest, ForexPrice, make_forex_price_request

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ForexPriceLoader(ABC):
    def __init__(self, path: str, api_key: str):
        self.path = path
        self.api_key = api_key

    @abstractmethod
    def download(req: ForexPriceRequest) -> ForexPrice:  # TODO[refactor]: change to just df
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
            logger.warning("data is None, meaning it has not been downloaded")
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
