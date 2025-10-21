import os
import sys
import signal

from dataclasses import dataclass
from itertools import permutations
import random
import time
import datetime

import pandas as pd
from dotenv import load_dotenv 
from urllib3.exceptions import MaxRetryError
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


def load_polygon_forex_price(req: ForexPriceRequest, path: str) -> ForexPrice:
    filename = f"{path}/{req.ticker}.csv"
    df = pd.read_csv(filename, index_col="timestamp", parse_dates=True)
    return ForexPrice(df, req)


def fetch_price(ticker: str, api_key: str, path: str):
    """pretty much git fetch, but for polygon data"""
    today = datetime.datetime.now()
    start = today - datetime.timedelta(730)
    req = ForexPriceRequest(ticker, start, today)

    data = download_polygon_forex_price(req, api_key)
    if not data:
        raise ValueError("Data is None, not downloaded")

    # TODO: outer join with old data
    save_polygon_forex_price(data, path)


def make_pairs(currencies: list[str]):
    priority = {
        "EUR": 9,
        "SEK": 8,
        "NOK": 7,
        "GBP": 6,
        "AUD": 5,
        "NZD": 4,
        "USD": 3,
        "CAD": 2,
        "CHF": 1,
        "JPY": 0
    }
    pairs = []
    for a, b in permutations(currencies, 2):
        pa = priority.get(a, -1)
        pb = priority.get(b, -1)
        if pa > pb:
            pairs.append(a + b)
    return pairs


def sigint_handler(sig, frame):
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    load_dotenv()
    api_key = os.getenv("POLYGON_API_KEY")
    path = ".polygon_cache"

    # currencies = ["AUD", "CAD", "EUR", "JPY", "NZD", "NOK", "GBP", "SEK", "CHF", "USD", "THB"]
    currencies = ["THB", "JPY", "SEK"]
    tickers = make_pairs(currencies)
    for ticker in tickers:
        ticker_2 = ticker[3:] + ticker[:3]

        filename = f"{path}/{ticker}.csv"
        filename_2 = f"{path}/{ticker_2}.csv"
        if os.path.exists(filename):
            print(f"We already have {filename} ; Skipping.")
            continue
        if os.path.exists(filename_2):
            print(f"We already have {filename_2} ; Skipping.")
            continue

        use_2 = False
        for attempt in range(3):
            try:
                if use_2:
                    ticker = ticker_2
                print(f"Fetching {ticker} (attempt {attempt + 1})...")
                fetch_price(ticker, api_key, path)
                time.sleep(5)
                break
            except MaxRetryError as e:
                wait = 30
                print(f"Error: {e} ; retrying in {wait:.1f}s...")
                time.sleep(wait)
            except ValueError as e:
                if use_2:
                    print(f"{ticker} or {ticker_2} is not available ; Skipping.")  # TODO: would be nice to remember what exotic pairs are not available
                    break
                use_2 = True
                print(f"Error: empty data ; retrying with {ticker_2}")
                time.sleep(3)
