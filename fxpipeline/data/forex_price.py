from dataclasses import dataclass
import datetime

import pandas as pd

from currencies import CurrencyPair


@dataclass
class ForexPriceRequest:
    pair: CurrencyPair
    start: datetime.datetime
    end: datetime.datetime
    tf_length: int = 1
    tf_unit: str = "day"  # minute, day, week, month

    def __str__(self) -> str:
        start = self.start.strftime("%Y-%m-%d %H:%M:%S")
        end = self.end.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.pair}[{start}, {end}]"
    
    def copy(self) -> "ForexPriceRequest":
        return ForexPriceRequest(self.pair, self.start, self.end)


def make_forex_price_request(ticker: str, days=365) -> ForexPriceRequest:
    today = datetime.datetime.now()
    start = today - datetime.timedelta(days)
    return ForexPriceRequest(CurrencyPair(ticker), start, today)


@dataclass
class ForexPrice:
    df: pd.DataFrame
    req: ForexPriceRequest  # remember the 'order' of this dish
