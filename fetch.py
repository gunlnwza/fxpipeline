import sys
import logging
import argparse
from itertools import combinations

from dotenv import load_dotenv

from fxpipeline.core import make_pair, CurrencyPair
from fxpipeline.ingestion import fetch_forex_prices
from fxpipeline.utils import handle_sigint

logger = logging.getLogger(__name__)


def config_logging(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )

    logging_levels = {
        logging.DEBUG: (),
        logging.INFO: (
            "requests",
            "yfinance",
            "peewee",
            "urllib3",
            "charset_normalizer",
        ),
        logging.WARNING: (),
        logging.ERROR: (),
    }
    for level, packages in logging_levels.items():
        for p in packages:
            logging.getLogger(p).setLevel(level)


def parse_tickers(tickers: list[str]) -> list[CurrencyPair]:
    if tickers[0] in ("major", "minor"):
        assert len(tickers) == 1, f"Invalid ticker list {tickers}"

    global_curs = ("EUR", "GBP", "AUD", "NZD", "CAD", "CHF", "JPY")
    if tickers[0] == "major":
        return [make_pair(a + "USD") for a in global_curs]
    elif tickers[0] == "minor":
        return [make_pair(a + b) for a, b in combinations(global_curs, 2)]
    return [make_pair(t) for t in tickers]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="+")
    parser.add_argument("-s", "--source", default="alpha_vantage")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    handle_sigint()
    config_logging(args.debug)

    try:
        pairs = parse_tickers(args.tickers)
    except (AssertionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    fetch_forex_prices(pairs, args.source, args.start, args.end)


if __name__ == "__main__":
    main()
