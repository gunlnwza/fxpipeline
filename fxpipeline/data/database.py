import os

from dotenv import load_dotenv 

from loaders import ForexPriceLoader, PolygonForex, AlphaVantageForex, YahooFinanceForex


class Database:
    """
    Connect to database or sth
    """
    def __init__(self):
        pass


load_dotenv()
LOADERS = {
    "alpha_vantage": AlphaVantageForex(".alpha_vantage_cache", os.getenv("ALPHA_VANTAGE_API_KEY")),
    "polygon": PolygonForex(".polygon_cache", os.getenv("POLYGON_API_KEY")),
    "yahoo_finance": YahooFinanceForex(".yahoo_finance_cache")
}
def get_loader(source: str = "yahoo_finance") -> ForexPriceLoader:
    """
    Factory method for loaders
    """
    if source not in LOADERS:
        raise ValueError(f"{source} is not a supported loader")
    return LOADERS[source]


def load_price(ticker: str, source: str = "alpha_vantage"):
    """
    Load existing price from cache 
    """

    loader = get_loader(source)
    loader.load_every_row(ticker)
