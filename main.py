import logging

from fxpipeline.data import load_forex_price, get_loader
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

    from fxpipeline.data import ForexPriceRequest, CurrencyPair
    import datetime

    import sys

    ticker = sys.argv[1]
    source = sys.argv[2]
    loader = get_loader(source)
    req = ForexPriceRequest(CurrencyPair(ticker), 
                          datetime.datetime(2025, 10, 10),
                          datetime.datetime(2025, 10, 30))
    loader.fetch(req)


if __name__ == "__main__":
    main()
