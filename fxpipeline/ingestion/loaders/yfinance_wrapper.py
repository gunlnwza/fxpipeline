import logging
import warnings

import pandas as pd
import yfinance as yf

from .base import ForexPriceLoader, BatchDownloadMixin
from ..data_request import ForexPriceRequest

logger = logging.getLogger(__name__)


class YFinanceForex(ForexPriceLoader, BatchDownloadMixin):
    def __init__(self, api_key=None):
        super().__init__(api_key)

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.droplevel("Ticker")
        df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"}, inplace=True)
        df = df[["open", "high", "low", "close", "volume"]]
        df.index.name = "timestamp"
        return df

    def download(self, req: ForexPriceRequest) -> pd.DataFrame:
        logger.info(f"Downloading '{req}' with yfinance")

        ticker = f"{req.ticker}=X"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            df = yf.download(ticker, req.start, req.end, progress=False)

        df = self._clean(df)
        return df

    @staticmethod
    def _batch_clean(df: pd.DataFrame) -> pd.DataFrame:
        df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"}, inplace=True)
        df.index.name = "timestamp"
        return df

    def batch_download(self, reqs: list[ForexPriceRequest]) -> list[pd.DataFrame]:
        logger.info(f"Downloading '{[r.ticker for r in reqs]}' with yfinance")

        tickers = [f"{r.ticker}=X" for r in reqs]
        start = min(r.start for r in reqs)
        end = max(r.end for r in reqs)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore")
            df = yf.download(tickers, start, end, group_by="ticker", progress=False)

        df = self._batch_clean(df)
        lst = [df[ticker] for ticker in tickers]
        return lst
