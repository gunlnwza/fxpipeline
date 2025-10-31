import os
import logging
import datetime
from pathlib import Path
from abc import ABC, abstractmethod

import pandas as pd

from ..core import ForexPriceRequest

logger = logging.getLogger(__name__)


class ForexPriceDatabase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, *args):
        """Save the given DataFrame"""
        pass

    @abstractmethod
    def load(self, *args) -> pd.DataFrame:
        """Load and return as DataFrame"""
        pass

    @abstractmethod
    def have(self, *args) -> bool:
        """Return True if there is the wanted data in cache"""
        pass

    @abstractmethod
    def is_up_to_date(self, *args) -> bool:
        """Return True if the wanted data is fresh"""
        pass


class CSVDatabase(ForexPriceDatabase):
    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def save(self, df: pd.DataFrame, ticker: str):
        os.makedirs(self.path, exist_ok=True)
        filename = f"{self.path}/{ticker}.csv"
        df.to_csv(filename)
        logger.info(f"Save data to '{filename}'")

    def load(self, ticker: str) -> pd.DataFrame:
        filename = f"{self.path}/{ticker}.csv"
        return pd.read_csv(filename, index_col="timestamp", parse_dates=True)

    def have(self, req: ForexPriceRequest) -> bool:
        filename = f"{self.path}/{req.pair}.csv"
        if os.path.exists(filename):
            return True
        return False
    
    def is_up_to_date(self, ticker: str, buffer_days=7) -> bool:
        df = self.load(ticker)
        last_datetime = df.index[-1].to_pydatetime()
        return last_datetime + datetime.timedelta(buffer_days) >= datetime.datetime.now()


def get_database(source: str = "alpha_vantage", method: str = "csv"):
    CACHES_PATH = Path(__file__).parent.absolute()
    path = f"{CACHES_PATH}/.{source}_cache"
    return CSVDatabase(path)
