from dataclasses import dataclass

import pandas as pd

from .currency import CurrencyPair


@dataclass
class ForexPrice:
    pair: CurrencyPair
    source: str
    df: pd.DataFrame
