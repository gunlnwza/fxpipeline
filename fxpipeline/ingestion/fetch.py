import logging
import time
import datetime

import pandas as pd
from urllib3.exceptions import MaxRetryError

from .loaders import get_loader
from .database import get_database
from .data import ForexPriceRequest, CurrencyPair

"""Fetch functions: fetching smartly and respectfully."""

logger = logging.getLogger(__name__)


def _download(loader, req: ForexPriceRequest):
    df = loader.download(req)
    if df is None:
        logger.warning(f"{req} is not downloaded.")
        return None
    logger.info(f"Load data for '{req}'")
    return df


def _fetch(req: ForexPriceRequest, source: str) -> bool:
    """Fetch one time. Updating the cache"""
    loader = get_loader(source)
    database = get_database(source)

    if database.is_up_to_date(req.ticker, buffer_days=7):
        logger.info(f"{req.ticker} is up to date.")
        return True

    # TODO[refactor]
    if database.have(req.ticker):
        old_df = database.load(req.pair.ticker)
        if len(old_df) == 0:
            df = _download(loader, req)
            if df is None:
                return False
            database.save(df, req.pair.ticker)
            return True

        last_datetime = old_df.index[-1].to_pydatetime()
        req = ForexPriceRequest(req.pair, last_datetime, req.end)
        df = _download(loader, req)
        if df is None:
            return False
        df = pd.concat([old_df, df], ignore_index=False)
        df = df[~df.index.duplicated(keep="last")]
        logger.info(f"Update data for '{req}'")
        return True
    else:
        df = _download(loader, req)
        if df is None:
            return False
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


def fetch_forex_price(ticker: str, days: int, source: str):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days)
    req = ForexPriceRequest(CurrencyPair(ticker), start, now)
    _fetch_with_retries(req, source)
