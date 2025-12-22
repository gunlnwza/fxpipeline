import logging
import warnings

import pandas as pd
import yfinance as yf

from ..base import ForexPriceLoader
from ...core import CurrencyPair, ForexPrices


logger = logging.getLogger(__name__)


class YFinanceForex(ForexPriceLoader):
    def __init__(self):
        super().__init__("yfinance", None)

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.droplevel("Ticker")
        df.columns.name = None
        df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            },
            inplace=True,
        )
        df.index.name = "timestamp"
        return df

    def download(
        self,
        pair: CurrencyPair,
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str = "1d",
    ) -> ForexPrices:
        logger.debug(f"Downloading {pair} with yfinance")

        ticker = f"{pair}=X"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            df = yf.download(ticker, start, end, group_by="ticker", progress=False)

        df = self._clean(df)
        return ForexPrices(pair.copy(), self.name, df)

    @staticmethod
    def _batch_clean(df: pd.DataFrame) -> pd.DataFrame:
        df.columns.names = (None, None)
        df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            },
            inplace=True,
        )
        df.index.name = "timestamp"
        return df

    def batch_download(
        self,
        pairs: list[CurrencyPair],
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str = "D1",
    ) -> list[ForexPrices]:
        logger.debug(f"Downloading {[pair.ticker for pair in pairs]} with yfinance")

        tickers = [f"{pair}=X" for pair in pairs]
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            df = yf.download(tickers, start, end, group_by="ticker", progress=False)

        df = self._batch_clean(df)
        return [
            ForexPrices(pair.copy(), self.name, df[ticker])
            for pair, ticker in zip(pairs, tickers)
        ]
