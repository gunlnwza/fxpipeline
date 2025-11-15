import logging
import argparse

from fxpipeline.ingestion import fetch_forex_price
from fxpipeline.utils import handle_sigint

logger = logging.getLogger(__name__)


def config_logging(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler()]
    )

    logging_levels = {
        logging.DEBUG: (),
        logging.INFO: ("requests", "yfinance", "peewee", "urllib3", "charset_normalizer"),
        logging.WARNING: (),
        logging.ERROR: ()
    }
    for level, packages in logging_levels.items():
        for p in packages:
            logging.getLogger(p).setLevel(level)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    # parser.add_argument("tickers", nargs="+")
    parser.add_argument("-s", "--source", default="yfinance")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--debug", action="store_false")
    args = parser.parse_args()

    handle_sigint()
    config_logging(args.debug)

    # tickers = args.tickers
    # if args.tickers == ["major"]:
    # tickers = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]

    data = fetch_forex_price(args.ticker, args.source, args.start, args.end)
    print(data)

if __name__ == "__main__":
    main()
