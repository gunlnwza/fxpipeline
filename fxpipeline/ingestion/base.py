import logging
from abc import ABC, abstractmethod

import pandas as pd

from ..core import CurrencyPair, ForexPrices

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message="API error"):
        super().__init__(message)


class NotDownloadedError(Exception):
    def __init__(self, message="Not downloaded"):
        super().__init__(message)


class ForexPriceLoader(ABC):
    def __init__(self, name: str, api_key: str):
        self.name = name
        self.api_key = api_key

    @abstractmethod
    def download(
        self,
        pair: CurrencyPair,
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str = "1d",
    ) -> ForexPrices:
        """Download forex data from internet, can raise errors"""

    def batch_download(
        self,
        pairs: list[CurrencyPair],
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str = "1d",
    ) -> list[ForexPrices]:
        """
        Call download() in a loop.
        But, concrete class like YFinanceForex may optimize.
        """
        res = []
        for pair in pairs:
            data = self.download(pair, start, end, interval)
            res.append(data)
        return res


class ForexPriceDatabase(ABC):
    @abstractmethod
    def save(self, data: ForexPrices):
        """Save `data`, append to table, overwrite existing rows"""

    @abstractmethod
    def load(
        self,
        pair: CurrencyPair,
        source: str,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
    ) -> ForexPrices:
        """Load historical data of `pair` in range [`start`, `end`]"""

    @abstractmethod
    def have(
        self, pair: CurrencyPair, source: str, start: pd.Timestamp, end: pd.Timestamp
    ) -> bool:
        """True if have `source`'s `pair` with datetimes [`start`, `end`]"""

    @abstractmethod
    def last_price(self, pair: CurrencyPair, source: str) -> float:
        """Get only last price of `pair`"""

    @abstractmethod
    def last_timestamp(self, pair: CurrencyPair, source: str) -> pd.Timestamp:
        """Get only last timestamp of `pair`"""
