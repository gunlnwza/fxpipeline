import logging
import warnings
from typing import TYPE_CHECKING

import pandas as pd
import yfinance as yf

from .base import ForexPriceLoader, ForexPriceRequest

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


class YahooFinanceForex(ForexPriceLoader):
    def __init__(self, path):
        super().__init__(path, None)

    def download(self, req: ForexPriceRequest) -> pd.DataFrame:
        # download
        ticker = self._convert_to_yf_ticker(req.pair)
        # warnings.filterwarnings("ignore")
        df = yf.download(ticker, req.start, req.end, progress=False)
        # warnings.filterwarnings("default")
        
        # df = yf.download(ticker, req.start, req.end)

        # clean
        df.columns = df.columns.droplevel("Ticker")
        df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"}, inplace=True)
        df.index.name = "timestamp"

        return df
