import logging
from abc import ABC, abstractmethod

import pandas as pd

from ...core import CurrencyPair, ForexPrice

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NotDownloadedError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ForexPriceLoader(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def download(self, ticker: CurrencyPair, start: pd.Timestamp,
                 end: pd.Timestamp, interval: str = "1d") -> ForexPrice:
        """Download forex data from internet, can raise errors"""

    def batch_download(self, tickers: list[CurrencyPair], start: pd.Timestamp,
                       end: pd.Timestamp, interval: str = "1d") -> list[ForexPrice]:
        """
        Call download() in a loop.
        But, Concrete class like YFinanceForex may optimize.
        """
        res = []
        for ticker in tickers:
            data = self.download(ticker, start, end, interval)
            res.append(data)
        return res
