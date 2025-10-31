import logging
import time
import datetime

import pandas as pd
from urllib3.exceptions import MaxRetryError

from .core import ForexPriceRequest, CurrencyPair
from .loaders import get_loader
from .database import get_database

"""Fetch functions: fetching smartly and respectfully."""

logger = logging.getLogger(__name__)


# TODO[download]: if the behavior were really like git's, it should not care about start and end dates
def _fetch(req: ForexPriceRequest, source: str) -> bool:
    """Fetch one time. Updating the cache"""
    loader = get_loader(source)
    database = get_database(source)

    # TODO[download]: inspect time range before concluding that we need to load from cache
    # if database.have(req):
    #     logger.info(f"Requested data ({req}) is up to date.")
    #     return True

    df = loader.download(req)
    if df is None:
        logger.warning(f"Data ({req}) is not downloaded.")
        return False

    # TODO[download]: subtract time range and only download the really needed newer portion
    if database.have(req):
        old_df = database.load(req.pair.ticker)
        df = pd.concat([old_df, df], ignore_index=False)
        df = df[~df.index.duplicated(keep="last")]
        logger.info(f"Update data for '{req}'")
 
    database.save(df, req.pair.ticker)
    return True


def _fetch_with_retries(req: ForexPriceRequest, source: str, retries=5, max_retry_wait=30) -> bool:
    """Fetch several times, update nothing if no data is downloaded"""
    logger.info(f"Fetching {req.pair}...")
    for i in range(1, retries + 1):
        try:
            logger.debug(f"Fetching {req.pair} (attempt {i})...")
            _fetch(req, source)
            return True
        except MaxRetryError as e:
            logger.error(f"MaxRetryError: {e} ; retrying in {max_retry_wait:.1f}s...")
            if i == retries:
                break
            time.sleep(max_retry_wait)
    return False


def fetch_forex_price(ticker: str, source: str = "alpha_vantage", days=100):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days)
    req = ForexPriceRequest(CurrencyPair(ticker), start, now)
    _fetch_with_retries(req, source)
