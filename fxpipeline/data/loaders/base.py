import os
import logging
import time
import random
from abc import ABC, abstractmethod

import pandas as pd
from urllib3.exceptions import MaxRetryError

from ..core import ForexPriceRequest

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ForexPriceLoader(ABC):
    def __init__(self, path: str, api_key: str):
        self.path = path
        self.api_key = api_key

    @abstractmethod
    def download(req: ForexPriceRequest) -> pd.DataFrame:
        """Download forex data from internet, can raise APIError"""
        pass

    def fetch(self, req: ForexPriceRequest):
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
