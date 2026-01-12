import sys
import logging
import argparse
from itertools import combinations

from dotenv import load_dotenv

from fxpipeline.core import make_pair, CurrencyPair
from fxpipeline.ingestion import fetch_forex_prices
from fxpipeline.utils import handle_sigint
from fxpipeline.commands.fetch import register_fetch
from fxpipeline.commands.simulate import register_simulate

logger = logging.getLogger(__name__)


def config_logging():
    logging.basicConfig(
        level=logging.DEBUG,
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
    load_dotenv()
    handle_sigint()
    config_logging()

    parser = argparse.ArgumentParser(prog="fxpipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_fetch(subparsers)
    register_simulate(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
