from abc import ABC, abstractmethod
import os
from typing import Optional

from dotenv import load_dotenv

# from alpha_vantage_data import 
from fxpipeline.data.dont_like.polygon_data import PolygonExtractor, PolygonTransformer, PolygonLoader
from fxpipeline.data.dont_like.yahoo_finance_data import YahooFinanceExtractor, YahooFinanceTransformer, YahooFinanceLoader

import pandas as pd


class DataCache(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def save(self, *args):
        pass

    @abstractmethod
    def load(self, *args) -> pd.DataFrame:
        pass

    @abstractmethod
    def exists(self, req) -> True:
        pass

    @abstractmethod
    def is_stale(self, *args) -> bool:
        pass


def load_data(req, source: str, cache: Optional[DataCache] = None):
    if cache and req in cache and not cache.is_stale(req):
        return cache.load()

    # select source, polymorphism in practice, fuck yeah
    match source:
        # case "alpha_vantage":
            # fetcher = AlphaVantageExtractor()
            # cleaner = AlphaVantageTransformer()
        case "polygon":
            fetcher = PolygonExtractor()
            cleaner = PolygonTransformer()
        case "yahoo_finance":
            fetcher = YahooFinanceExtractor()
            cleaner = YahooFinanceTransformer()
        case _:
            raise ValueError("Not supported")
        
    # SOURCES = {
    #     "polygon": (PolygonExtractor, PolygonTransformer),
    #     "yahoo_finance": (YahooFinanceExtractor, YahooFinanceTransformer),
    #     # ...
    # }

    # fetcher_cls, transformer_cls = SOURCES[source]
    # fetcher = fetcher_cls()
    # cleaner = transformer_cls()
            
    df = fetcher.fetch(req)
    df = cleaner.clean(df)

    if cache:
        cache.save(df)

    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", type=str)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()

    load_dotenv("../../.env")
    loader = PolygonLoader(os.getenv("POLYGON_API_KEY"))
    # prices = loader.load(args.ticker, args.start, args.end)
    prices = loader.load(args.ticker)
    print(prices)
