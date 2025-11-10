import pandas as pd

from .database import get_database
from ..core import make_pair, ForexPrice


def load_forex_price(ticker: str, source: str = "alpha_vantage") -> ForexPrice:
    """Load price from local cache"""
    database = get_database(source)
    try:
        df = database.load(ticker)
        return ForexPrice(make_pair(ticker), df)
    except FileNotFoundError as e:
        print("Error:", e)
        return None
