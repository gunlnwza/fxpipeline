import os
import logging
import requests
from io import StringIO

import pandas as pd

from core import ForexPriceRequest, ForexPrice, CurrencyPair

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AlphaVantageAPIError(Exception):
    """Raised when Alpha Vantage returns an error response instead of expected CSV"""
    pass

def download_alpha_vantage_forex_price(req: ForexPriceRequest, api_key: str, full=False) -> ForexPrice:
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
        "apikey": api_key,
        "from_symbol": req.pair.base,
        "to_symbol": req.pair.quote,
        "function": "FX_DAILY",
        "datatype": "csv",
        "outputsize": "full" if full else "compact"
    }

    res = requests.get("https://www.alphavantage.co/query", params, timeout=10)
    if not res.ok:
        raise requests.exceptions.HTTPError(f"HTTP {res.status_code} — cannot download {req}")

    content_type = res.headers.get("Content-Type", "")
    if content_type and "json" in content_type.lower():
        msg = res.json()
        raise AlphaVantageAPIError(f"Asked for csv, but got json, likely an error message: {msg}")

    df = pd.read_csv(StringIO(res.text), index_col="timestamp", parse_dates=True)
    df = df.sort_index()
    return ForexPrice(df, req)


def save_alpha_vantage_forex_price(data: ForexPrice, path: str):
    os.makedirs(path, exist_ok=True)
    filename = f"{path}/{data.req.pair}.csv"
    data.df.to_csv(filename)
    logger.info(f"Save data to '{filename}'")


def load_alpha_vantage_forex_price(req: ForexPriceRequest, path: str) -> ForexPrice:
    filename = f"{path}/{req.pair}.csv"
    df = pd.read_csv(filename, index_col="timestamp", parse_dates=True)
    return ForexPrice(df, req)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    load_dotenv("../../.env")
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    # TODO: must unify the separate data store for each of the sources
    # I have decided it is best to cache the data sources separately, like storing all raw ingredients in fridge
    path = ".alpha_vantage_cache"

    # TODO: can only download compact (100 rows), or full
    # but if download full, then don't throw away excess, cache them
    ticker = "AUDJPY"
    req = ForexPriceRequest(CurrencyPair(ticker), "2023-01-01", "2026-01-01")

    filename = f"{path}/{ticker}.csv"
    if os.path.exists(filename):
        data = load_alpha_vantage_forex_price(req, path)
    else:
        data = download_alpha_vantage_forex_price(req, api_key, full=True)
        save_alpha_vantage_forex_price(data, path)
    print(data.df)
