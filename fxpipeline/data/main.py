import os
import logging

from dotenv import load_dotenv 

from signal_utils import handle_sigint
from currencies import MAJOR_CURRENCIES, G10_CURRENCIES, EXOTIC_CURRENCIES, EMERGING_MARKET_CURRENCIES
from loaders import ForexPriceLoader, PolygonForex, AlphaVantageForex, YahooFinanceForex

logger = logging.getLogger(__name__)


load_dotenv()
LOADERS = {
    "alpha_vantage": AlphaVantageForex(".alpha_vantage_cache", os.getenv("ALPHA_VANTAGE_API_KEY")),
    "polygon": PolygonForex(".polygon_cache", os.getenv("POLYGON_API_KEY")),
    "yahoo_finance": YahooFinanceForex(".yahoo_finance_cache")
}
def get_loader(name: str) -> ForexPriceLoader:
    if name not in LOADERS:
        raise ValueError(f"{name} is not a supported loader")
    return LOADERS[name]


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

    loader = get_loader("alpha_vantage")
    loader.fetch_all_pairs(currencies=G10_CURRENCIES)


if __name__ == "__main__":
    main()
