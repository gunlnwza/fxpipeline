import logging
# import warnings

import pandas as pd
import yfinance as yf

from .base import ForexPriceLoader, ForexPriceRequest

logger = logging.getLogger(__name__)


class YFinanceForex(ForexPriceLoader):
    def __init__(self):
        super().__init__(None)

    def download(self, req: ForexPriceRequest) -> pd.DataFrame:
        # download
        ticker = self._convert_to_yf_ticker(req.pair)
        # warnings.filterwarnings("ignore")  # yfinance's peewee might forgot to close db
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
