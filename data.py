from abc import ABC, abstractmethod
import pandas as pd
import os
from pathlib import Path
from typing import Optional
import yfinance as yf

"""
ETL Architecture, fuck yeah
"""


class DataExtractor(ABC):
    """Download 😇 or scrape 😈 from any source"""
    @abstractmethod
    def fetch(self, *args, **kwargs):
        pass


class DataTransformer(ABC):
    """
    Validate and clean data from DataExtractor
    """
    @abstractmethod
    def clean(self, *args, **kwargs):
        pass


class DataLoader(ABC):
    """Load from local cache"""
    @abstractmethod
    def load(self, *args, **kwargs):
        pass


# ---

class TestExtractor(DataExtractor):
    def __init__(self):
        super().__init__()

    def fetch(self, ticker):
        df = yf.download(ticker)
        return df
    

class TestTransformer(DataTransformer):
    def __init__(self):
        super().__init__()

    def clean(self, df: pd.DataFrame):
        df = df.droplevel("Ticker", axis=1)
        return df


class TestLoader(DataLoader):
    """Just a test"""
    def __init__(self):
        super().__init__()

    def load(self, ticker: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
        # TODO: make sqlite db, or use pickle?

        # TODO: find filename intelligently, save cache's dir name?
        filename = Path("test_cache") / f"{ticker}.csv"
        if not os.path.exists(filename):
            # fallback: call extractor → transformer → save file
            # TODO: delegate to extractor and transformer, then try loading again
            raise FileNotFoundError(f"{filename} not found. Run extractor?")

        df = pd.read_csv(filename, parse_dates=True, index_col="Date")
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]
        return df


def get_prices(ticker: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    ticker = ticker.upper()

    loader = TestLoader()
    try:
        df = loader.load(ticker, start, end)
    except FileNotFoundError:
        extractor = TestExtractor()
        df = extractor.fetch(ticker)
        transormer = TestTransformer()
        df = transormer.clean(df)
        filename = Path("test_cache") / f"{ticker}.csv"
        df.to_csv(filename)
    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", type=str)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()

    prices = get_prices(args.ticker, args.start, args.end)
    print(prices)
