import logging
import datetime

from fxpipeline.data import load_forex_price, get_loader

from fxpipeline.data.forex_price import ForexPriceRequest
from fxpipeline.data.currency_pair import CurrencyPair

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

    # l = get_loader("alpha_vantage")
    # l.fetch(ForexPriceRequest(CurrencyPair("USDTHB"), datetime.datetime(2025, 10, 10), datetime.datetime(2025, 10, 30)))

    df = load_forex_price("USDTHB")
    print(df)


if __name__ == "__main__":
    main()
