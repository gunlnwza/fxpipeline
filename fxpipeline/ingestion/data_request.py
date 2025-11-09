from dataclasses import dataclass

import pandas as pd

from ..core import CurrencyPair


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


def make_forex_price_request(ticker: str, days=365) -> ForexPriceRequest:
    today = pd.Timestamp.now()
    start = today - pd.Timedelta(days=days)
    return ForexPriceRequest(CurrencyPair(ticker), start, today)
