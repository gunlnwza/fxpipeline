import os
import logging
from ..utils import Stopwatch

import pandas as pd
from dotenv import load_dotenv

from .loaders import get_loader
from .database import SQLiteDatabase
from ..core import ForexPrice, make_pair, CurrencyPair

load_dotenv()
CACHES_PATH = os.getenv("CACHES_PATH")
logger = logging.getLogger(__file__)


def _convert_pairs(pairs: str | CurrencyPair | list[str | CurrencyPair]) -> list[CurrencyPair]:
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


def fetch_forex_prices(pairs: str | CurrencyPair | list[str | CurrencyPair], source: str,
                       start: str | pd.Timestamp | None = None,
                       end: str | pd.Timestamp | None = None) -> list[ForexPrice]:
    print(f"📦 Fetching with {source.upper()} API")
    sw_0 = Stopwatch()

    pairs = _convert_pairs(pairs)
    start, end = _convert_start_end(start, end, 30)

    db = SQLiteDatabase(f"{CACHES_PATH}/prices.db")
    loader = get_loader(source)
    res = []

    for pair in pairs:
        print(f"📈 {pair} [{source}]... ", end="", flush=True)
        if db.have(pair, source, start, end):
            logger.debug(f"Have {source}'s {pair} in cache")
            data = db.load(pair, source)
            print("✅ Cached")
        else:
            sw_1 = Stopwatch()
            data = loader.download(pair, start, end)
            db.save(data)
            print(f"⏱️  {sw_1.time:.2f}s")
        res.append(data)

    db.close()
    print(f"✔️  All done in {sw_0.time:.2f}s")
    return res


def load_forex_prices(pairs: str | CurrencyPair | list[str | CurrencyPair], source: str,
                      start: str | pd.Timestamp | None = None,
                      end: str | pd.Timestamp | None = None) -> list[ForexPrice]:
    pairs = _convert_pairs(pairs)
    start, end = _convert_start_end(start, end, 10000)

    db = SQLiteDatabase(f"{CACHES_PATH}/prices.db")
    res = [db.load(pair, source, start, end) for pair in pairs]
    db.close()
    return res
