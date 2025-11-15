import logging
import argparse
from itertools import combinations

from fxpipeline.core import make_pair
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
    parser.add_argument("tickers", nargs="+")
    parser.add_argument("-s", "--source", default="yfinance")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--debug", action="store_false")
    args = parser.parse_args()

    handle_sigint()
    config_logging(args.debug)

    global_curs = ("EUR", "GBP", "AUD", "NZD", "CAD", "CHF", "JPY")
    if args.tickers == ["major"]:
        pairs = [make_pair(a + "USD") for a in global_curs]
    elif args.tickers == ["minor"]:
        pairs = [make_pair(a + b) for a, b in combinations(global_curs, 2)]
    else:
        pairs = [make_pair(t) for t in args.tickers]

    data = fetch_forex_price(pairs[0], args.source, args.start, args.end)
    print(data)


if __name__ == "__main__":
    main()
