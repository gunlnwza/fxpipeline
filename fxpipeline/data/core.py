from itertools import combinations
from dataclasses import dataclass

import pandas as pd


@dataclass
class ForexPriceRequest:
    ticker: str
    start: str
    end: str


@dataclass
class ForexPrice:
    df: pd.DataFrame
    req: ForexPriceRequest  # remember the 'order' of this dish


class CurrencyPair:
    currencies_ordering = [
        "EUR", "SEK", "NOK", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "JPY", "THB"
    ]
    priority = {}
    for i, cur in enumerate(currencies_ordering):
        priority[cur] = len(currencies_ordering) - i

    def __init__(self, cur_1: str, cur_2: str):
        cur_1 = cur_1.upper()
        cur_2 = cur_2.upper()
        if CurrencyPair.priority.get(cur_1, -1) > CurrencyPair.priority.get(cur_2, -1):
            cur_1, cur_2 = cur_2, cur_1

        self.cur_1 = cur_1
        self.cur_2 = cur_2

    @property
    def ticker(self):
        return self.cur_1 + self.cur_2
    
    @property
    def reverse_ticker(self):
        return self.cur_2 + self.cur_1

    def __repr__(self):
        return f"CurrencyPair({self.cur_1}, {self.cur_2})"

    def __str__(self):
        return self.ticker    


def make_pairs(currencies: list[str]) -> list[CurrencyPair]:
    return [CurrencyPair(cur_1, cur_2) for cur_1, cur_2 in combinations(currencies, 2)]
