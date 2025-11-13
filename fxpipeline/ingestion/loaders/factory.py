import os
from dotenv import load_dotenv

from .base import ForexPriceLoader
from .alpha_vantage import AlphaVantageForex
from .massive import MassiveForex
from .yfinance_wrapper import YFinanceForex

load_dotenv()

LOADERS = {
    "alpha_vantage": AlphaVantageForex(os.getenv("ALPHA_VANTAGE_API_KEY")),
    "massive": MassiveForex(os.getenv("POLYGON_API_KEY")),
    "yfinance": YFinanceForex()
}


def get_loader(source: str) -> ForexPriceLoader:
    if source not in LOADERS:
        raise ValueError(f"{source} is not a supported loader")
    return LOADERS[source]
