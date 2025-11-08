import logging
from io import StringIO
import requests

import numpy as np
import pandas as pd

from .base import ForexPriceLoader, APIError, ForexPriceRequest

logger = logging.getLogger(__name__)


class AlphaVantageForex(ForexPriceLoader):
    def __init__(self, api_key):
        super().__init__(api_key)

    @staticmethod
    def _should_download_full(req: ForexPriceRequest):
        business_day = np.busday_count(req.start.date(), req.end.date() + pd.Timedelta(days=1))
        return business_day >= 100

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_index()
        return df

    def download(self, req: ForexPriceRequest) -> pd.DataFrame:
        """
        download price from Alpha Vantage
        return df on success, None on error

        Parameters
        [REQUIRED] `apikey`:
        [REQUIRED] `from_symbol`:
        [REQUIRED] `to_symbol`:
        [REQUIRED] `function`: FX_INTRADAY, FX_DAILY, FX_WEEKLY, FX_MONTHLY

        [REQUIRED if FX_INTRADAY] `interval`: 1min, 5min, 15min, 30min, 60min

        [OPTIONAL] `datatype`: default=json, csv
        [OPTIONAL if FX_INTRADAY, FX_DAILY] `outputsize`: default=compact, full

        NOTE: 4H is not supported by the API
        """
        params = {
            "apikey": self.api_key,
            "from_symbol": req.pair.base,
            "to_symbol": req.pair.quote,
            "function": "FX_DAILY",
            "datatype": "csv",
            "outputsize": "full" if self._should_download_full(req) else "compact"
        }
        logger.debug("Alpha Vantage, downloading with option: " + params["outputsize"])

        res = requests.get("https://www.alphavantage.co/query", params, timeout=10)
        if not res.ok:
            logger.error(f"HTTP {res.status_code} — cannot download {req}")
            return None

        content_type = res.headers.get("Content-Type", "")
        if content_type and "json" in content_type.lower():
            msg = res.json()
            raise APIError(f"Alpha Vantage API error: {msg}")

        df = pd.read_csv(StringIO(res.text), index_col="timestamp", parse_dates=True)
        df = self._clean(df)
        return df
