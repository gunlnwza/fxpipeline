import logging

from fxpipeline.data import fetch_forex_price, load_forex_price, make_pairs, MAJOR_CURRENCIES, CurrencyPair
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

    # pairs = make_pairs(MAJOR_CURRENCIES)
    # pairs = make_pairs(["EUR", "USD"])
    # for pair in pairs:
        # fetch_forex_price(pair.ticker, "yahoo_finance", 1500)
    fetch_forex_price("GBPAUD", 100)

if __name__ == "__main__":
    main()
