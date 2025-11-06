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
    parser.add_argument("ticker")
    parser.add_argument("days", type=int, default=100)
    args = parser.parse_args()

    fetch_forex_price(args.ticker, args.days)


if __name__ == "__main__":
    main()
