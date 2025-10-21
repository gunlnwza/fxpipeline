import os
import sys
import signal

import time
import datetime

from dotenv import load_dotenv 
from urllib3.exceptions import MaxRetryError

from core import ForexPriceRequest, make_pairs, CurrencyPair
from polygon_data import download_polygon_forex_price, save_polygon_forex_price


def sigint_handler(sig, frame):
    print()
    sys.exit(0)


def fetch_price(ticker: str, api_key: str, path: str):
    """pretty much git fetch, but for polygon data"""
    today = datetime.datetime.now()
    start = today - datetime.timedelta(730)
    req = ForexPriceRequest(ticker, start, today)

    data = download_polygon_forex_price(req, api_key)
    if not data:
        raise ValueError("Data is None, meaning is has not been downloaded")

    # TODO: outer join with old data
    # load old data
    # pd.join()
    # save
    save_polygon_forex_price(data, path)


def attempt_fetch(ticker, retries=3, max_retry_wait=20):
    """attempting to fetch for several times"""

    for attempt in range(1, retries + 1):
        try:
            print(f"Fetching {ticker} (attempt {attempt})...")
            fetch_price(ticker, api_key, path)
            return True
        except MaxRetryError as e:
            print(f"Error: {e} ; retrying in {max_retry_wait:.1f}s...")
            time.sleep(max_retry_wait)

    return False


def fetch_all_pairs(currencies):
    pairs: list[CurrencyPair] = make_pairs(currencies)
    for pair in pairs:
        filename = f"{path}/{pair.ticker}.csv"
        if os.path.exists(filename):
            print(f"We already have '{filename}' ; Skipping.")
            continue

        success = attempt_fetch(pair.ticker)
        if success:
            continue
        success = attempt_fetch(pair.reverse_ticker)
        if not success:
            print(f"Warning: No data available for '{pair.ticker}', perhaps too exotic")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    load_dotenv()
    api_key = os.getenv("POLYGON_API_KEY")
    path = ".polygon_cache"

    # TODO: would be nice to remember what exotic pairs are not available
    currencies = ["AUD", "CAD", "EUR", "JPY", "NZD", "NOK", "GBP", "SEK", "CHF", "USD", "THB"]
    fetch_all_pairs(currencies)
