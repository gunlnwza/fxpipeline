from dataclasses import dataclass
import datetime

import pandas as pd

from currencies import CurrencyPair


@dataclass
class ForexPriceRequest:
    pair: CurrencyPair
    start: datetime.datetime
    end: datetime.datetime

    def __str__(self) -> str:
        start = self.start.strftime("%Y-%m-%d %H:%M:%S")
        end = self.end.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.pair}[{start}, {end}]"


@dataclass
class ForexPrice:
    df: pd.DataFrame
    req: ForexPriceRequest  # remember the 'order' of this dish
