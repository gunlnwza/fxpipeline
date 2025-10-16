from .alpha_vantage_api import AlphaVantageAPI
from .cache import Cache
from ..core import PriceRequest, Data
from ..utils import PrettyLogger

log = PrettyLogger("forex")


# TODO: generalize to Macro and Stocks data later
def load_data(req: PriceRequest) -> Data:
    """ultimate client-facing fa-ca-de"""

    cache = Cache()
    if cache.have(req):
        log.info("Using Cache")
        return cache.load(req)
    else:
        loader = AlphaVantageAPI()  # or Polygon, or Oanda, or ...
        data = loader.load(req)
        path = cache.save(data)
        log.info(f"Save csv to '{path}'")
        return data
