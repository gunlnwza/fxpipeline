from dataclasses import dataclass

import pandas as pd

from currencies import CurrencyPair


@dataclass
class ForexPriceRequest:
    pair: CurrencyPair
    start: str
    end: str


@dataclass
class ForexPrice:
    df: pd.DataFrame
    req: ForexPriceRequest  # remember the 'order' of this dish
