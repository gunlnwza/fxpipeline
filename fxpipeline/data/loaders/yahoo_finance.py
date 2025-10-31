import logging
import warnings
from typing import TYPE_CHECKING

import pandas as pd
import yfinance as yf

from .base import ForexPriceLoader
from ..core import CurrencyPair, ForexPriceRequest

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


class YahooFinanceForex(ForexPriceLoader):
    def __init__(self, path):
        super().__init__(path, None)

    def _convert_to_yf_ticker(self, pair: CurrencyPair) -> str:
        # TODO[fix]: be careful with-USD pairs, it seems most are quoted in USDXXX
        if pair.base == "USD":
            return f"{pair.quote}=X"
        elif pair.quote == "USD":
            return f"{pair.base}=X"

        return f"{pair.ticker}=X"

    def download(self, req: ForexPriceRequest) -> pd.DataFrame:
        # download
        ticker = self._convert_to_yf_ticker(req.pair)
        # warnings.filterwarnings("ignore")
        df = yf.download(ticker, req.start, req.end, progress=False)
        # warnings.filterwarnings("default")

        # clean
        df.columns = df.columns.droplevel("Ticker")
        df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"}, inplace=True)
        df.index.name = "timestamp"

        return df
