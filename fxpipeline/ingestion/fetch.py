import os

import pandas as pd
from dotenv import load_dotenv

from .loaders import get_loader
from .database import SQLiteDatabase
from ..core import ForexPrice, make_pair

load_dotenv()

CACHES_PATH = os.getenv("CACHES_PATH")


def fetch_forex_price(ticker: str, source: str,
                      start: str | None = None,
                      end: str | None = None) -> ForexPrice:
    pair = make_pair(ticker)

    if end is None:
        end = pd.Timestamp.now()
    if start is None:
        start = end - pd.Timedelta(days=30) 
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    db = SQLiteDatabase(f"{CACHES_PATH}/prices.db")
    if db.have(pair, source, start, end):
        return db.load(ticker, source)

    loader = get_loader(source)
    data = loader.download(pair, start, end)
    db.save(data)


# I like retry logic

# def _fetch_with_retries(reqs: list[],
#                         loader: ForexPriceLoader,
#                         database: ForexPriceDatabase,
#                         retries=5, max_retry_wait=30) -> bool:
#     """Fetch several times, update nothing if no data is downloaded"""
#     for req in reqs:
#         logger.debug(f"Fetching {req.pair}...")
#         for i in range(1, retries + 1):
#             try:
#                 logger.debug(f"Fetching {req.pair} (attempt {i})...")
#                 _fetch(req, loader, database)  # Can raise exceptions.
#                 break
#             except MaxRetryError as e:
#                 logger.error(f"MaxRetryError: {e} ; retrying in {max_retry_wait:.1f}s...")
#                 if i == retries:
#                     break
#                 time.sleep(max_retry_wait)
