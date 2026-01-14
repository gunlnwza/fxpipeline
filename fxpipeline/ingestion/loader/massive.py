import logging
import time

import pandas as pd
from urllib3.exceptions import MaxRetryError
from polygon import RESTClient
from polygon.exceptions import BadResponse as PolygonBadResponse

from ..base import ForexPriceLoader
from ..error import APIError
from ...core import CurrencyPair, ForexPrices

logger = logging.getLogger(__name__)


class MassiveForex(ForexPriceLoader):
    """Polygon rebranded themselves as Massive"""

    def __init__(self, api_key):
        super().__init__("massive", api_key)

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df.index = pd.to_datetime(df["timestamp"], unit="ms")
        for name in ("vwap", "timestamp", "transactions", "otc"):
            df.drop(name, axis=1, inplace=True)
        return df

    def download(
        self,
        pair: CurrencyPair,
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str = "1d",
    ) -> ForexPrices:
        logger.debug(f"Downloading {pair} with Massive API")

        aggs = None
        client = RESTClient(self.api_key)
        time_wait = 1
        while not aggs:
            try:
                aggs = list(client.list_aggs(f"C:{pair}", 1, "day", start, end, adjusted="true", sort="asc"))
            except MaxRetryError:
                time_wait *= 2
                time.sleep(time_wait)
            except PolygonBadResponse as e:
                raise APIError(e)

        df = pd.DataFrame(aggs)
        df = self._clean(df)
        return ForexPrices(pair.copy(), self.name, df)
