from abc import ABC, abstractmethod
import pandas as pd

"""
ETL Architecture, fuck yeah
"""


class DataExtractor(ABC):
    """Download 😇 or scrape 😈 from any source"""
    @abstractmethod
    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        pass


class DataTransformer(ABC):
    """Validate and clean data from DataExtractor"""
    @abstractmethod
    def clean(self, df: pd.DataFrame, *args, **kwargs):
        pass


class DataLoader(ABC):
    """Save and Load from local cache"""
    @abstractmethod
    def save(self, df: pd.DataFrame, *args, **kwargs):
        """save data to cache"""
        pass

    @abstractmethod
    def read(self, *args, **kwargs) -> pd.DataFrame:
        """read data from cache"""
        pass

    @abstractmethod
    def load(self, *args, **kwargs) -> pd.DataFrame:
        """
        if data doesn't exist: use extractor and transformer, save()
        else: read()
        """
        pass
