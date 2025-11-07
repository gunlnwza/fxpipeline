import os
from pathlib import Path
from dotenv import load_dotenv

from .base import ForexPriceLoader
from .alpha_vantage import AlphaVantageForex
from .polygon import PolygonForex
from .yahoo_finance import YahooFinanceForex

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


def get_loader(source: str) -> ForexPriceLoader:
    """Factory method for loaders"""
    if source not in LOADERS:
        raise ValueError(f"{source} is not a supported loader")
    return LOADERS[source]
