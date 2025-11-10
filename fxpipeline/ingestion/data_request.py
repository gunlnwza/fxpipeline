from dataclasses import dataclass

import pandas as pd

from ..core import make_pair, CurrencyPair


@dataclass
class ForexPriceRequest:
    pair: CurrencyPair
    start: pd.Timestamp
    end: pd.Timestamp
    tf_length: int = 1
    tf_unit: str = "day"  # minute, day, week, month

    @property
    def ticker(self):
        return self.pair.ticker

    def __str__(self) -> str:
        start = self.start.strftime("%Y-%m-%d %H:%M:%S")
        end = self.end.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.pair}[{start}, {end}]"

    def copy(self) -> "ForexPriceRequest":
        return ForexPriceRequest(self.pair, self.start, self.end)


def make_data_request(ticker: str, start: str, end: str) -> ForexPriceRequest:
    return ForexPriceRequest(make_pair(ticker), pd.Timestamp(start), pd.Timestamp(end))


def make_recent_data_request(ticker: str, days=365) -> ForexPriceRequest:
    today = pd.Timestamp.now()
    start = today - pd.Timedelta(days=days)
    return ForexPriceRequest(make_pair(ticker), start, today)
