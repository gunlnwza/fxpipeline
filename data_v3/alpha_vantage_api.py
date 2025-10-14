import os
from io import StringIO

import requests
import pandas as pd
from dotenv import load_dotenv

from .loader import Loader
from ..core import PriceRequest, Data, PriceMetaData
from ..utils import PrettyLogger

load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

log = PrettyLogger("forex")


# TODO: download with "full" if first time or too old,
# else if it's fresh (< 3 months), just use "compact"
class AlphaVantageAPI(Loader):
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_API_KEY
        pass

    def _get_function(self, unit: str) -> str:
        match unit:
            case "m" | "h": return "FX_INTRADAY"
            case "D": return "FX_DAILY"
            case "W": return "FX_WEEKLY"
            case "M": return "FX_MONTHLY"
            case _: raise ValueError(
                f"cannot map '{unit}' to Alpha Vantage Function")

    def _get_params(self, req: PriceRequest, outputsize: str) -> dict:
        func = self._get_function(req.timeframe.unit)

        params = {
            "apikey": self.api_key,
            "from_symbol": req.ticker.from_symbol,
            "to_symbol": req.ticker.to_symbol,
            "function": func,
            "datatype": "csv",
        }
        if func == "FX_INTRADAY":
            params["interval"] = req.timeframe.length
        if func in ("FX_INTRADAY", "FX_DAILY"):
            params["outputsize"] = outputsize

        return params

    def _download_forex_price(self, req: PriceRequest,
                              *, outputsize="compact") -> pd.DataFrame:
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

        # TODO: make the Exceptions more specific
        # load and check for all errors
        try:
            base_url = "https://www.alphavantage.co/query"
            params = self._get_params(req, outputsize)
            res = requests.get(base_url, params, timeout=10)
            if not res.ok:
                raise Exception(
                    f"HTTP {res.status_code} — cannot download {req}")

            # AlphaVantage “error” message
            # (JSON with 'Information' or 'Error Message')
            content_type = res.headers.get("Content-Type", "")
            if content_type and "json" in content_type.lower():
                try:
                    msg = res.json()
                    words = ("Error Message", "Information", "Note")
                    if any(word in msg for word in words):
                        raise Exception(f"Alpha Vantage error: {msg}")
                except Exception:
                    raise Exception("Unexpected JSON response")
        except requests.RequestException as e:
            raise Exception(f"Network error fetching {req}: {e}")

        try:
            df = pd.read_csv(
                StringIO(res.text), index_col="timestamp", parse_dates=True)
            df = df.sort_index()
            return df
        except Exception as e:
            raise Exception(f"Failed to parse CSV for {req}: {e}")

    def load(self, req: PriceRequest) -> Data:
        log.info("Using Alpha Vantage API")
        df = self._download_forex_price(req)
        metadata = PriceMetaData(req.ticker, req.timeframe)
        return Data(df, metadata)
