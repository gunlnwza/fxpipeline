import logging
from abc import ABC, abstractmethod

import pandas as pd

from ..data import ForexPriceRequest

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
    def download(req: ForexPriceRequest) -> pd.DataFrame:
        """Download forex data from internet, can Errors"""
        pass
