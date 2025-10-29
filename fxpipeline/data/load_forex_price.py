import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from .loaders import ForexPriceLoader, PolygonForex, AlphaVantageForex, YahooFinanceForex

load_dotenv()
CACHES_PATH = Path(__file__).parent.absolute()
LOADERS = {
    "alpha_vantage": AlphaVantageForex(
        f"{CACHES_PATH}/.alpha_vantage_cache",
        os.getenv("ALPHA_VANTAGE_API_KEY")
    ),
    "polygon": PolygonForex(
        f"{CACHES_PATH}/.polygon_cache",
        os.getenv("POLYGON_API_KEY")
    ),
    "yahoo_finance": YahooFinanceForex(
        f"{CACHES_PATH}/.yahoo_finance_cache"
    )
}


def get_loader(source: str = "yahoo_finance") -> ForexPriceLoader:
    """
    Factory method for loaders
    """
    if source not in LOADERS:
        raise ValueError(f"{source} is not a supported loader")
    return LOADERS[source]


def load_forex_price(ticker: str, source: str = "alpha_vantage") -> pd.DataFrame:
    """
    Load existing price from cache 
    """
    loader = get_loader(source)
    try:
        df = loader.load_every_row(ticker)
        return df
    except FileNotFoundError as e:
        print("Error:", e)
        return None
