import os
import logging
from pathlib import Path
from abc import ABC, abstractmethod

import pandas as pd

from .core import ForexPriceRequest

logger = logging.getLogger(__name__)


class ForexPriceDatabase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, *args):
        pass

    @abstractmethod
    def load(self, *args) -> pd.DataFrame:
        pass

    @abstractmethod
    def have(self, *args) -> bool:
        """Return True if there is the wanted data in cache"""


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

    def have_in_cache(self, req: ForexPriceRequest) -> bool:  # TODO[implementation]: also include time
        filename = f"{self.path}/{req.pair}.csv"
        if os.path.exists(filename):
            return True
        return False


def get_database(source: str = "alpha_vantage", method: str = "csv"):
    CACHES_PATH = Path(__file__).parent.absolute()
    path = f"{CACHES_PATH}/.{source}_cache"
    return CSVDatabase(path)
