import os
import logging

import pandas as pd
from dotenv import load_dotenv

from .loaders import get_loader
from .database import SQLiteDatabase
from ..core import ForexPrice, make_pair, CurrencyPair

load_dotenv()

CACHES_PATH = os.getenv("CACHES_PATH")

logger = logging.getLogger(__file__)


def fetch_forex_price(ticker: str | CurrencyPair, source: str,
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
        logger.debug(f"Have {source}'s {pair} in cache")
        return db.load(pair, source)

    loader = get_loader(source)
    data = loader.download(pair, start, end)
    db.save(data)
    return data
