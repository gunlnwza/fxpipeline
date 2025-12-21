import logging
import time

import pandas as pd
from urllib3.exceptions import MaxRetryError
from polygon import RESTClient

from ..base import ForexPriceLoader, NotDownloadedError
from ...core import CurrencyPair, ForexPrice

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
    ) -> ForexPrice:
        logger.debug(f"Downloading {pair} with Massive API")

        aggs = None
        client = RESTClient(self.api_key)
        retries = 3
        time_wait = 10
        for i in range(retries):
            try:
                logger.debug(f"Downloading (attempt={i + 1})")
                aggs = list(
                    client.list_aggs(
                        f"C:{pair}", 1, "day", start, end, adjusted="true", sort="asc"
                    )
                )
                break
            except MaxRetryError:
                if i == retries - 1:
                    break
                logger.debug(
                    f"Massive API limit exceeded (attempt={i + 1}), "
                    f"retrying in {time_wait}s"
                )
                time_wait *= 2
                time.sleep(time_wait)

        if aggs is None:
            raise NotDownloadedError("Massive: data is not downloaded")

        df = pd.DataFrame(aggs)
        df = self._clean(df)
        return ForexPrice(pair.copy(), self.name, df)
