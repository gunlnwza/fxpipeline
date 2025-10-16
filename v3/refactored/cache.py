import os

import pandas as pd

from .loader import Loader
from ..utils import PrettyLogger
from ..core import PriceRequest, Data, PriceMetaData

# TODO: Track Start-End range
# TODO: Track source
# TODO: Handle stale data

log = PrettyLogger("forex")


# Cache is a loader with special abilities
# - save
# - manage cache
class Cache(Loader):
    def __init__(self):
        self.dir = ".cache"
        os.makedirs(self.dir, exist_ok=True)
        log.debug(f"Make directory '{self.dir}'")

    def get_csv_path(self, filename: str) -> str:
        return f"{self.dir}/{filename}.csv"

    def load(self, req: PriceRequest) -> Data:
        path = self.get_csv_path(req.str)
        df = pd.read_csv(path, index_col="timestamp", parse_dates=True)
        metadata = PriceMetaData(req.ticker, req.timeframe)
        return Data(df, metadata)

    def save(self, data: Data) -> str:
        # TODO: it would just know what type of data it is, and act accordingly
        filename = data.metadata.str
        path = self.get_csv_path(filename)
        data.df.to_csv(path)
        return path

    def have(self, req: PriceRequest) -> bool:
        path = self.get_csv_path(req.str)
        return os.path.isfile(path)
