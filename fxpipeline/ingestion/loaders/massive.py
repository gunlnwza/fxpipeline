import logging
import pandas as pd

from polygon import RESTClient

from .base import ForexPriceLoader, NotDownloadedError

logger = logging.getLogger(__name__)


class MassiveForex(ForexPriceLoader):
    """Polygon rebranded themselves as Massive"""

    def __init__(self, api_key):
        super().__init__(api_key)

    @staticmethod
    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        df.index = pd.to_datetime(df["timestamp"], unit="ms")
        for name in ("timestamp", "transactions", "otc"):
            df.drop(name, axis=1, inplace=True)
        return df

    def download(self, req, start, end, interval) -> pd.DataFrame:
        logger.info(f"Downloading '{req} with Massive API")

        aggs = []
        client = RESTClient(self.api_key)
        for a in client.list_aggs(
            f"C:{req.pair}", 1, "day", req.start, req.end, adjusted="true", sort="asc"
        ):
            aggs.append(a)

        if not aggs:
            raise NotDownloadedError("Massive: data is not downloaded")

        df = pd.DataFrame(aggs)
        df = self._clean(df)
        return df
