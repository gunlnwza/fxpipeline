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
    """Save and Load from local cache"""
    @abstractmethod
    def save(self, *args, **kwargs):
        pass

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


# TODO: try out sqlite, parquet, or pickle?
class TestLoader(DataLoader):
    """Just a test"""
    def __init__(self):
        super().__init__()

    def get_filename(self, ticker: str):
        return Path("test_cache") / f"{ticker}.csv"

    def save(self, df: pd.DataFrame, ticker: str):
        filename = self.get_filename(ticker)
        df.to_csv(filename)

    def load(self, ticker: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
        

        filename = self.get_filename(ticker)
        have_data = os.path.exists()  # TODO: also pay attention to time
        if not have_data:
            extractor = TestExtractor()
            transormer = TestTransformer()
            df = extractor.fetch(ticker)
            df = transormer.clean(df)
            self.save(df, ticker)

        df = pd.read_csv(filename, parse_dates=True, index_col="Date")
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]
        return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", type=str)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()

    loader = TestLoader()
    prices = loader.load(args.ticker, args.start, args.end)
    print(prices)
