import logging
import warnings

import pandas as pd
import yfinance as yf

from .base import ForexPriceLoader, ForexPriceRequest

logger = logging.getLogger(__name__)


class YFinanceForex(ForexPriceLoader):
    def __init__(self):
        super().__init__(None)

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

        warnings.filterwarnings("ignore")  # NOTE: yfinance's peewee might forget to close db
        df = yf.download(f"{req.ticker}=X", req.start, req.end, progress=False)
        warnings.filterwarnings("default")

        df = self._clean(df)
        return df

    def download_batch(self, reqs: list[ForexPriceRequest]):
        # optimization, download all tickers at once
        raise NotImplementedError
