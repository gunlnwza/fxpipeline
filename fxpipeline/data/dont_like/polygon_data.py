from datetime import date

import pandas as pd
from polygon import RESTClient

from fxpipeline.data.dont_like.base import DataExtractor, DataTransformer, DataLoader


class PolygonExtractor(DataExtractor):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

    def fetch(self, ticker: str, start: str, end: str):
        client = RESTClient(self.api_key)
        aggs = []
        for a in client.list_aggs(f"C:{ticker}", 1, "day", start, end,
                                  adjusted="true", sort="asc"):
            aggs.append(a)
        return pd.DataFrame(aggs)


class PolygonTransformer(DataTransformer):
    def clean(self, df):
        df.index = pd.to_datetime(df["timestamp"], unit="ms")

        df.drop("timestamp", axis=1, inplace=True)
        df.drop("transactions", axis=1, inplace=True)
        df.drop("otc", axis=1, inplace=True)

        return df


class PolygonLoader(DataLoader):
    def __init__(self, api_key: str):
        super().__init__()
        self.extractor = PolygonExtractor(api_key)
        self.transformer = PolygonTransformer()

    def save(self):
        pass

    def read(self):
        pass

    def load(self, ticker: str, start="2023-01-01", end=date.today()):
        df = self.extractor.fetch(ticker, start, end)
        df = self.transformer.clean(df)
        return df
