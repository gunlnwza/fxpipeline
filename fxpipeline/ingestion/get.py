import os
import logging

import pandas as pd
from dotenv import load_dotenv

from .loaders import get_loader
from .database import SQLiteDatabase
from ..core import ForexPrice, make_pair, CurrencyPair

load_dotenv()
logger = logging.getLogger(__file__)
db = SQLiteDatabase(f"{os.getenv("CACHES_PATH")}/prices.db")


def _convert_pairs(pairs: str | CurrencyPair | list[str | CurrencyPair]) -> list[CurrencyPair]:
    if isinstance(pairs, str) or isinstance(pairs, CurrencyPair):
        return [make_pair(pairs)]
    else:
        return [make_pair(p) for p in pairs]


def _convert_start_end(start, end):
    if end is None:
        end = pd.Timestamp.now()
    if start is None:
        start = end - pd.Timedelta(days=30)
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return start, end


def fetch_forex_prices(pairs: str | CurrencyPair | list[str | CurrencyPair], source: str,
                       start: str | pd.Timestamp | None = None,
                       end: str | pd.Timestamp | None = None) -> list[ForexPrice]:
    pairs = _convert_pairs(pairs)
    start, end = _convert_start_end(start, end)

    loader = get_loader(source)
    res = []
    for pair in pairs:
        if db.have(pair, source, start, end):
            logger.debug(f"Have {source}'s {pair} in cache")
            data = db.load(pair, source)
        else:
            data = loader.download(pair, start, end)
            db.save(data)
        res.append(data)

    return res


def load_forex_prices(pairs: str | CurrencyPair | list[str | CurrencyPair], source: str,
                      start: str | pd.Timestamp | None = None,
                      end: str | pd.Timestamp | None = None) -> list[ForexPrice]:
    pairs = _convert_pairs(pairs)
    start, end = _convert_start_end(start, end)

    res = [db.load(pair, source, start, end) for pair in pairs]
    return res
