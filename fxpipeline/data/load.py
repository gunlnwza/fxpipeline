import pandas as pd

from .database import get_database


def load_forex_price(ticker: str, source: str = "alpha_vantage") -> pd.DataFrame:
    """Load price from local cache"""
    database = get_database(source)
    try:
        df = database.load(ticker)
        return df
    except FileNotFoundError as e:
        print("Error:", e)
        return None
