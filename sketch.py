import os
import datetime
from dataclasses import dataclass

import pandas as pd
from dotenv import load_dotenv 

from polygon import RESTClient


@dataclass
class ForexPriceRequest:
    ticker: str
    start: str
    end: str

@dataclass
class ForexPrice:
    df: pd.DataFrame
    req: ForexPriceRequest  # remember the 'order' of this dish


def get_polygon_forex_price(req: ForexPriceRequest, api_key: str) -> ForexPrice:
    # download
    client = RESTClient(api_key)
    aggs = []
    for a in client.list_aggs(
        f"C:{req.ticker}", 1, "day", req.start, req.end,
        adjusted="true", sort="asc"
    ):
        aggs.append(a)

    # clean
    df = pd.DataFrame(aggs)
    df.index = pd.to_datetime(df["timestamp"], unit="ms")
    for name in ("timestamp", "transactions", "otc"):
        df.drop(name, axis=1, inplace=True)

    return ForexPrice(df, req)


def save_polygon_forex_price(data: ForexPrice, path: str):
    os.makedirs(path, exist_ok=True)
    filename = f"{path}/{data.req.ticker}.csv"
    data.df.to_csv(filename)


def load_polygon_forex_price(req: ForexPriceRequest, path: str) -> ForexPrice:
    filename = f"{path}/{req.ticker}.csv"
    df = pd.read_csv(filename, index_col="timestamp", parse_dates=True)
    return ForexPrice(df, req)


if __name__ == "__main__":
    today = datetime.datetime.now()
    start = today - datetime.timedelta(730)  # free tier only give latest 2 years data
    req = ForexPriceRequest("EURUSD", start, today)

    load_dotenv()
    api_key = os.getenv("POLYGON_API_KEY")

    # data = get_polygon_forex_price(req, api_key)
    # print(data)
    # save_polygon_forex_price(data, ".polygon_cache")
    # print("Save to cache")

    print("Load from cache")
    data = load_polygon_forex_price(req, ".polygon_cache")
    print(data)
