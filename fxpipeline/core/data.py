from dataclasses import dataclass

import pandas as pd

from .currency import CurrencyPair


@dataclass
class ForexPrice:
    pair: CurrencyPair
    df: pd.DataFrame
