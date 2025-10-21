import os
import logging

import pandas as pd
from polygon import RESTClient

from core import ForexPriceRequest, ForexPrice

logger = logging.getLogger(__name__)


def download_polygon_forex_price(req: ForexPriceRequest, api_key: str) -> ForexPrice:
    # download
    client = RESTClient(api_key)
    aggs = []
    for a in client.list_aggs(
        f"C:{req.ticker}", 1, "day", req.start, req.end,
        adjusted="true", sort="asc"
    ):
        aggs.append(a)

    if not aggs:
        return None

    df = pd.DataFrame(aggs)
    df.index = pd.to_datetime(df["timestamp"], unit="ms")
    for name in ("timestamp", "transactions", "otc"):
        df.drop(name, axis=1, inplace=True)

    return ForexPrice(df, req)


def save_polygon_forex_price(data: ForexPrice, path: str):
    os.makedirs(path, exist_ok=True)
    filename = f"{path}/{data.req.ticker}.csv"
    data.df.to_csv(filename)
    logger.info(f"Save data to '{filename}'")


def load_polygon_forex_price(req: ForexPriceRequest, path: str) -> ForexPrice:
    filename = f"{path}/{req.ticker}.csv"
    df = pd.read_csv(filename, index_col="timestamp", parse_dates=True)
    return ForexPrice(df, req)
