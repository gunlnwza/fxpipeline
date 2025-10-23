import os
import logging

from dotenv import load_dotenv 

from signal_utils import handle_sigint
from currencies import MAJOR_CURRENCIES
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
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    for package in ("urllib3", "io", "charset_normalizer", "chardet", "yfinance"):
        logging.getLogger(package).setLevel(logging.WARNING)
    logging.getLogger("loaders").setLevel(logging.DEBUG)


def main():
    handle_sigint()
    config_logging()

    loader = get_loader("yahoo_finance")
    loader.fetch_all_pairs(currencies=["EUR", "USD"])


if __name__ == "__main__":
    main()
