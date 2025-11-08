import logging
import time

import pandas as pd
from urllib3.exceptions import MaxRetryError

from .loaders import get_loader
from .database import get_database
from .data import ForexPriceRequest, CurrencyPair

"""Fetch functions: fetching smartly and respectfully."""

logger = logging.getLogger(__name__)


def _fetch(req: ForexPriceRequest, source: str) -> bool:
    """Fetch one time. Updating the cache"""
    t = req.ticker
    loader = get_loader(source)
    database = get_database(source)

    if database.is_up_to_date(t, buffer_days=7):
        logger.info(f"{t} is up to date.")
        return

    old_df = database.load(t) if database.have(t) else None
    if old_df is None or len(old_df) == 0:
        df = loader.download(req)
        logger.info(f"Download data for '{req}'")
        database.save(df, t)
        return

    last_datetime = old_df.index[-1].to_pydatetime()
    req = ForexPriceRequest(req.pair, last_datetime, req.end)
    df = loader.download(req)
    logger.info(f"Download data for '{req}'")

    df = pd.concat([old_df, df], ignore_index=False)
    df = df[~df.index.duplicated(keep="last")]
    logger.info(f"Update data for '{t}'")

    database.save(df, t)


def _fetch_with_retries(req: ForexPriceRequest, source: str, retries=5, max_retry_wait=30) -> bool:
    """Fetch several times, update nothing if no data is downloaded"""
    logger.info(f"Fetching {req.pair}...")
    for i in range(1, retries + 1):
        try:
            logger.debug(f"Fetching {req.pair} (attempt {i})...")
            _fetch(req, source)  # Can raise any errors. If that happens, try again.
            return
        except MaxRetryError as e:
            logger.error(f"MaxRetryError: {e} ; retrying in {max_retry_wait:.1f}s...")
            if i == retries:
                break
            time.sleep(max_retry_wait)


def fetch_forex_price(ticker: str, days: int, source: str):
    now = pd.Timestamp.now()
    start = now - pd.Timedelta(days=days)
    req = ForexPriceRequest(CurrencyPair(ticker), start, now)
    _fetch_with_retries(req, source)
