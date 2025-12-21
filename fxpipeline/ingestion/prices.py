import os
import logging
import time

import pandas as pd

from .factory import get_loader, get_database
from ..core import ForexPrice, CurrencyPair, make_pair
from ..utils import Stopwatch

CACHES_PATH = os.getenv("CACHES_PATH")
logger = logging.getLogger(__file__)


def _convert_pairs(
    pairs: str | CurrencyPair | list[str | CurrencyPair],
) -> list[CurrencyPair]:
    if isinstance(pairs, str) or isinstance(pairs, CurrencyPair):
        return [make_pair(pairs)]
    else:
        return [make_pair(p) for p in pairs]


def _convert_start_end(start, end, days):
    if end is None:
        end = pd.Timestamp.now()
    if start is None:
        start = end - pd.Timedelta(days=days)
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return start, end


def fetch_forex_prices(
    pairs: str | CurrencyPair | list[str | CurrencyPair],
    source: str,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> list[ForexPrice]:
    """
    Fetch prices from the internet and save to SQLite Cache.
    Ignore if already have the price.
    """
    pairs = _convert_pairs(pairs)
    start, end = _convert_start_end(start, end, 30)

    db = get_database("sqlite")
    loader = get_loader(source)
    res = []

    print(f"📦 Fetching with {source.upper()} API ({start.date()} to {end.date()})")
    fetch_time = Stopwatch()
    for pair in pairs:
        print(f"📈 {pair} [{source}]... ", end="", flush=True)
        if db.have(pair, source, start, end):
            logger.debug(f"Have {source}'s {pair} in cache")
            data = db.load(pair, source)
            print("✅ Cached")
        else:
            download_time = Stopwatch()
            data = loader.download(pair, start, end)
            db.save(data)
            print(f"⏱️  {download_time}")
            time.sleep(1)

        res.append(data)

    db.close()
    print(f"✔️  All done in {fetch_time}")
    return res


def load_forex_prices(
    pairs: str | CurrencyPair | list[str | CurrencyPair],
    source: str = "alpha_vantage",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> ForexPrice | list[ForexPrice]:
    """Load prices from local SQLite cache"""
    start, end = _convert_start_end(start, end, 10000)

    db = get_database("sqlite")
    res = [db.load(pair, source, start, end) for pair in _convert_pairs(pairs)]
    db.close()

    if isinstance(pairs, str) or isinstance(pairs, CurrencyPair):
        return res[0]
    return res
