import os
import sys
import signal
import time
import datetime
import logging

from dotenv import load_dotenv 
from urllib3.exceptions import MaxRetryError

from core import ForexPriceRequest, make_pairs, CurrencyPair
from polygon_data import download_polygon_forex_price, save_polygon_forex_price

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("polygon_data").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


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


def attempt_fetch(ticker, retries=5, max_retry_wait=30):
    """attempting to fetch for several times"""

    logger.info(f"Fetching {ticker}...")
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Fetching {ticker} (attempt {attempt})...")
            fetch_price(ticker, api_key, path)
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

        success = attempt_fetch(pair.ticker)
        if success:
            continue
        success = attempt_fetch(pair.reverse_ticker)
        if not success:
            logger.warning(f"No data available for '{pair.ticker}', perhaps too exotic")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    load_dotenv()
    api_key = os.getenv("POLYGON_API_KEY")
    path = ".polygon_cache"

    # TODO: would be nice to remember what exotic pairs are not available

    # currencies = ["AUD", "CAD", "EUR", "JPY", "NZD", "NOK", "GBP", "SEK", "CHF", "USD", "THB"]
    currencies = ["AUD", "EUR", "USD", "JPY", "GBP", "NZD", "CHF"]
    # currencies = ["AUD", "EUR", "USD"]
    # currencies = [""]
    fetch_all_pairs(currencies)
