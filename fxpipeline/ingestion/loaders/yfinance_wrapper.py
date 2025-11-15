import logging
import warnings

import pandas as pd
import yfinance as yf

from .base import ForexPriceLoader
from ...core import CurrencyPair, ForexPrice


logger = logging.getLogger(__name__)


class YFinanceForex(ForexPriceLoader):
    def __init__(self):
        super().__init__("yfinance", None)

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.droplevel("Ticker")
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index.name = "timestamp"
        return df

    def download(self, pair: CurrencyPair, start: pd.Timestamp,
                 end: pd.Timestamp, interval: str = "1d") -> ForexPrice:
        logger.info(f"Downloading '{pair}' with yfinance")

        ticker = f"{pair}=X"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            df = yf.download(ticker, start, end, group_by="ticker", progress=False)

        df = self._clean(df)
        return ForexPrice(pair.copy(), self.name, df)

    # @staticmethod
    # def _batch_clean(df: pd.DataFrame) -> pd.DataFrame:
    #     df.rename(columns={
    #         "Open": "open", "High": "high", "Low": "low",
    #         "Close": "close", "Volume": "volume"}, inplace=True)
    #     df.index.name = "timestamp"
    #     return df
    
    def batch_download(self, pairs: list[str], start: pd.Timestamp,
                       end: pd.Timestamp, interval: str = "D1") -> list[ForexPrice]:
        pass

    # def batch_download(self, reqs: list[str]) -> list[pd.DataFrame]:
    #     logger.info(f"Downloading '{[r.ticker for r in reqs]}' with yfinance")

    #     tickers = [f"{r.ticker}=X" for r in reqs]
    #     start = min(r.start for r in reqs)
    #     end = max(r.end for r in reqs)
    #     with warnings.catch_warnings(record=True):
    #         warnings.simplefilter("ignore")
    #         df = yf.download(tickers, start, end, group_by="ticker", progress=False)

    #     df = self._batch_clean(df)
    #     lst = [df[ticker] for ticker in tickers]
    #     return lst
