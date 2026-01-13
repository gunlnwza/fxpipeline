import sys
import logging

from fxpipeline.utils import parse_tickers
from fxpipeline.ingestion import fetch_forex_prices

logger = logging.getLogger(__name__)


def run(args):
    try:
        pairs = parse_tickers(args.tickers)
    except (AssertionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    fetch_forex_prices(
        pairs,
        args.source,
        args.start,
        args.end,
        args.forced
    )


def register_fetch(subparsers):
    parser = subparsers.add_parser("fetch", help="Fetch forex price data")
    parser.add_argument("tickers", nargs="*", default=["major"], help="list of tickers to fetch")
    parser.add_argument("-s", "--source", default="alpha_vantage", help="data source")
    parser.add_argument("--start", help="start date")
    parser.add_argument("--end", help="end date")
    parser.add_argument("-f", "--forced", action="store_true", help="force download")

    parser.set_defaults(func=run)
