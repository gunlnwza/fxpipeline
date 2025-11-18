from dataclasses import dataclass

import pandas as pd

from .currency import CurrencyPair


@dataclass
class ForexPrice:
    pair: CurrencyPair
    source: str
    df: pd.DataFrame

    @property
    def ticker(self):
        return self.pair.ticker

    def copy(self):
        return ForexPrice(self.pair, self.source, self.df.copy())
