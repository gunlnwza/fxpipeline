import logging
import pandas as pd

from polygon import RESTClient

from .base import ForexPriceLoader
from ..core import ForexPriceRequest

logger = logging.getLogger(__name__)


class PolygonForex(ForexPriceLoader):
    def __init__(self, path, api_key):
        super().__init__(path, api_key)

    def download(self, req: ForexPriceRequest) -> pd.DataFrame:
        # download
        aggs = []
        client = RESTClient(self.api_key)
        for a in client.list_aggs(
            f"C:{req.pair}", 1, "day", req.start, req.end,
            adjusted="true", sort="asc"
        ):
            aggs.append(a)
        if not aggs:
            return None

        # clean
        df = pd.DataFrame(aggs)
        df.index = pd.to_datetime(df["timestamp"], unit="ms")
        for name in ("timestamp", "transactions", "otc"):
            df.drop(name, axis=1, inplace=True)

        return df
