import os
import logging

from dotenv import load_dotenv 

from signal_utils import handle_sigint
from currencies import MAJOR_CURRENCIES
from loaders import PolygonForex, AlphaVantageForex, YahooForex

logger = logging.getLogger(__name__)


def main():
    handle_sigint()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    for package in ("urllib3", "io", "charset_normalizer", "chardet"):
        logging.getLogger(package).setLevel(logging.WARNING)
    logging.getLogger("loaders").setLevel(logging.DEBUG)

    load_dotenv()
    loader = AlphaVantageForex(".alpha_vantage_cache", os.getenv("ALPHA_VANTAGE_API_KEY"))
    # loader = PolygonForex(".polygon_cache", os.getenv("POLYGON_API_KEY"))
    # loader = YahooForex()

    loader.fetch_all_pairs(MAJOR_CURRENCIES, full=True)


if __name__ == "__main__":
    main()
