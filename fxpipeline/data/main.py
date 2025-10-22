import os
from signal_utils import handle_sigint

import time
import datetime
import logging

from dotenv import load_dotenv 
from urllib3.exceptions import MaxRetryError

from core import ForexPriceRequest, make_pairs, CurrencyPair


def fetch_price(pair: CurrencyPair, api_key: str, path: str):  # TODO: choose strategy at this function
    """pretty much git fetch, but for polygon data"""
    today = datetime.datetime.now()
    start = today - datetime.timedelta(730)
    req = ForexPriceRequest(pair, start, today)

    # data = download_polygon_forex_price(req, api_key)
    data = download_alpha_vantage_forex_price(req, api_key, full=True)
    if not data:
        raise ValueError("Data is None, meaning is has not been downloaded")

    # TODO: outer join with old data
    # load old data
    # pd.join()
    # save
    
    # save_polygon_forex_price(data, path)
    save_alpha_vantage_forex_price(data, path)


def attempt_fetch(pair: CurrencyPair, retries=5, max_retry_wait=30) -> bool:
    """attempting to fetch for several times"""

    logger.info(f"Fetching {pair.ticker}...")
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Fetching {pair.ticker} (attempt {attempt})...")
            fetch_price(pair, api_key, path)
            return True
        except MaxRetryError as e:
            logger.error(f"{e} ; retrying in {max_retry_wait:.1f}s...")
            if attempt < retries:
                time.sleep(max_retry_wait)

    return False


def fetch_all_pairs(currencies):
    pairs: list[CurrencyPair] = make_pairs(currencies)
    for pair in pairs:
        filename = f"{path}/{pair.ticker}.csv"
        if os.path.exists(filename):
            logger.debug(f"We already have '{filename}' ; Skipping")
            continue

        success = attempt_fetch(pair)
        if success:
            continue
        success = attempt_fetch(pair.reverse())
        if not success:
            logger.warning(f"No data available for '{pair.ticker}', perhaps too exotic")


def main():
    handle_sigint()

    avf = AlphaVantageForex(".alpha_vantage_cache", )
    pf = PolygonForex()
    yf = YahooForex()


if __name__ == "__main__":
    main()
