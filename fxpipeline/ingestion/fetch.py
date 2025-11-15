# I like retry logic

# def _fetch_with_retries(reqs: list[],
#                         loader: ForexPriceLoader,
#                         database: ForexPriceDatabase,
#                         retries=5, max_retry_wait=30) -> bool:
#     """Fetch several times, update nothing if no data is downloaded"""
#     for req in reqs:
#         logger.info(f"Fetching {req.pair}...")
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

import os

from dotenv import load_dotenv

from .loaders import get_loader
from .database import SQLiteDatabase
from ..core import ForexPrice


load_dotenv()


def fetch_forex_prices(ticker: str, source: str, start: str, end: str) -> list[ForexPrice]:
    loader = get_loader(source)
    db = SQLiteDatabase(os.getenv("CACHES_PATH"))

    if db.have(ticker, source, start, end):
        return
