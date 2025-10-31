import os
from pathlib import Path

from dotenv import load_dotenv

from .core import ForexPriceRequest
from .loaders import ForexPriceLoader, PolygonForex, AlphaVantageForex, YahooFinanceForex

"""Fetch functions: fetching smartly and respectfully."""

load_dotenv()
print(Path(__file__).parent)
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
    """Factory method for loaders"""
    if source not in LOADERS:
        raise ValueError(f"{source} is not a supported loader")
    return LOADERS[source]


def _fetch(req: ForexPriceRequest, source: str):
    """
    Fetch one time.
    """
    loader = get_loader(source)
    loader.download(req)


def fetch_forex_price(req: ForexPriceRequest, source: str):
    """
    Fetch several times, return nothing if no data is downloaded
    """
    for i in range(3):
        _fetch(req, source)
