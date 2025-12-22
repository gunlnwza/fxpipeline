from dataclasses import dataclass

import pandas as pd

from .currency import CurrencyPair


@dataclass
class ForexPrices:
    pair: CurrencyPair
    source: str
    df: pd.DataFrame
    # timeframe: ???

    @property
    def ticker(self):
        return self.pair.ticker

    def copy(self):
        return ForexPrices(self.pair, self.source, self.df.copy())

    def __len__(self):
        return len(self.df)


@dataclass
class PricePoint:
    timestamp: pd.Timestamp
    price: float
