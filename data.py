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

    def fetch(self, ticker, start, end):
        df = yf.download(ticker, start, end)
        return df
    

class TestTransformer(DataTransformer):
    def __init__(self):
        super().__init__()

    def clean(self, df: pd.DataFrame):
        df = df.droplevel("Ticker", axis=1)
        return df


# TODO: try out sqlite, parquet, or pickle?
class TestLoader(DataLoader):
    def __init__(self):
        super().__init__()
        self.extractor = TestExtractor()
        self.transformer = TestTransformer()

    def get_filename(self, ticker: str):
        return Path("test_cache") / f"{ticker}.csv"

    def save(self, df: pd.DataFrame, ticker: str):
        filename = self.get_filename(ticker)
        df.to_csv(filename)

    def download_full(self, ticker: str) -> pd.DataFrame:
        df = self.extractor.fetch(ticker, start="2015-01-01", end=None)
        df = self.transformer.clean(df)
        return df

    def read_from_cache(self, ticker: str):
        filename = self.get_filename(ticker)
        df = pd.read_csv(filename, parse_dates=True, index_col="Date")
        return df

    def update_if_stale(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        last_date = df.index[-1]
        today = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)

        if last_date >= today:
            return df  # Fresh enough

        # Fetch from next day after last_date
        fetch_start = last_date + pd.Timedelta(days=1)
        new_data = self.extractor.fetch(ticker, fetch_start, None)
        new_data = self.transformer.clean(new_data)

        if new_data is not None and not new_data.empty:
            df = pd.concat([df, new_data])
            df = df[~df.index.duplicated(keep='last')]  # Deduplicate just in case
            self.save(df, ticker)

        return df

    def load(self, ticker: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
        filename = self.get_filename(ticker)

        if not os.path.exists(filename):
            df = self.download_full(ticker)
            self.save(df, ticker)
        else:
            df = self.read_from_cache(ticker)
            df = self.update_if_stale(df, ticker)

        # Filter to start/end range
        if start:
            df = df[df.index >= pd.to_datetime(start)]
        if end:
            df = df[df.index <= pd.to_datetime(end)]
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
