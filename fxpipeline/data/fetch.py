from .core import ForexPriceRequest, make_pairs
from .get_loader import get_loader

"""
Fetch functions: fetching smartly and respectfully.
"""

def _fetch(req: ForexPriceRequest, source: str):
    """
    Fetch one time.
    """
    loader = get_loader(source)
    loader.download(req)


def fetch_forex_price(req: ForexPriceRequest, source: str):
    """
    Fetch several times, return nothing if no data is downloaded
    """
    for i in range(3):
        _fetch(req, source)



# These Should not be in here, too simple, not core functions

# def fetch_all_pairs(currencies: list[str], req):
#     for pair in make_pairs(currencies):
#         fetch_forex_price(req)

# def fetch_pair():
#     pass
