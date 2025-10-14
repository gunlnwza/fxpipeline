import os
from pathlib import Path
from typing import Optional
import yfinance as yf
import pandas as pd

from base import DataExtractor, DataLoader, DataTransformer


class TestExtractor(DataExtractor):
    def __init__(self):
        super().__init__()

    def fetch(self, ticker: str, start="2000-01-01", end=None):
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
        os.makedirs(filename.parent, exist_ok=True)
        df.to_csv(filename)

    def read(self, ticker: str) -> pd.DataFrame:
        filename = self.get_filename(ticker)
        df = pd.read_csv(filename, parse_dates=True, index_col="Date")
        return df

    def load(self, ticker: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        filename = self.get_filename(ticker)
        if not os.path.exists(filename):
            df = self.extractor.fetch(ticker)
            if len(df) == 0:
                return None
            df = self.transformer.clean(df)
            self.save(df, ticker)
        else:
            df = self.read(ticker)

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
