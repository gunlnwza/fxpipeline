import logging
import time

import pandas as pd
from urllib3.exceptions import MaxRetryError

from .loaders import get_loader, ForexPriceLoader, BatchDownloadMixin
from .database import get_database, ForexPriceDatabase
from .data_request import make_recent_data_request, ForexPriceRequest


"""Fetch functions: fetching smartly and respectfully."""

logger = logging.getLogger(__name__)


def _fetch(req: ForexPriceRequest,
           loader: ForexPriceLoader,
           database: ForexPriceDatabase) -> bool:
    """Fetch one time. Updating the cache"""
    t = req.ticker

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


def _batch_fetch(reqs: list[ForexPriceRequest],
                 loader: BatchDownloadMixin,
                 database: ForexPriceDatabase) -> bool:
    # TODO[ingestion]: modify individually each ForexPriceRequest before sending to batch_download
    df = loader.batch_download(reqs)
    print(df)


def _fetch_with_retries(reqs: list[ForexPriceRequest],
                        loader: ForexPriceLoader,
                        database: ForexPriceDatabase,
                        retries=5, max_retry_wait=30) -> bool:
    """Fetch several times, update nothing if no data is downloaded"""
    for req in reqs:
        logger.info(f"Fetching {req.pair}...")
        for i in range(1, retries + 1):
            try:
                logger.debug(f"Fetching {req.pair} (attempt {i})...")
                _fetch(req, loader, database)  # Can raise exceptions.
                return
            except MaxRetryError as e:
                logger.error(f"MaxRetryError: {e} ; retrying in {max_retry_wait:.1f}s...")
                if i == retries:
                    break
                time.sleep(max_retry_wait)


def fetch_forex_price(tickers: str | list[str], source: str, days: int = 365):
    if type(tickers) == str:
        reqs = [make_recent_data_request(tickers, days)]
    else:
        reqs = [make_recent_data_request(t, days) for t in tickers]
    loader = get_loader(source)
    database = get_database(source)

    if isinstance(loader, BatchDownloadMixin):
        logger.info(f"Fetching {reqs}...")
        _batch_fetch(reqs, loader, database)
    else:
        _fetch_with_retries(reqs, loader, database)
