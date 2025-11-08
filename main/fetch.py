import logging
import argparse

from fxpipeline.ingestion import fetch_forex_price
from fxpipeline.utils import handle_sigint

logger = logging.getLogger(__name__)


def config_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    logging_levels = {
        logging.DEBUG: ("loaders",),
        logging.INFO: ("yfinance", "peewee", "urllib3", "charset_normalizer"),
        logging.WARNING: ("requests",),
        logging.ERROR: ()
    }
    for level, packages in logging_levels.items():
        for p in packages:
            logging.getLogger(p).setLevel(level)


def main():
    handle_sigint()
    config_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="+")
    parser.add_argument("--days", type=int, default=100)
    parser.add_argument("--source", default="yfinance")
    args = parser.parse_args()

    for ticker in args.tickers:
        fetch_forex_price(ticker, args.days, args.source)


if __name__ == "__main__":
    main()
