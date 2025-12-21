import os

from .base import ForexPriceLoader, ForexPriceDatabase
from .loader import AlphaVantageForex, MassiveForex, YFinanceForex
from .database import SQLiteDatabase


def get_loader(source: str) -> ForexPriceLoader:
    match source:
        case "alpha_vantage":
            return AlphaVantageForex(os.getenv("ALPHA_VANTAGE_API_KEY"))
        case "massive":
            return MassiveForex(os.getenv("MASSIVE_API_KEY"))
        case "yfinance":
            return YFinanceForex()
        case _:
            raise ValueError(f"{source} is not a supported loader")


def get_database(db: str) -> ForexPriceDatabase:
    match db:
        case "sqlite":
            return SQLiteDatabase(os.getenv("DATABASE_PATH"))
