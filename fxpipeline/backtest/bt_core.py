from dataclasses import dataclass
from enum import Enum

import numpy as np

from ..core import CurrencyPair


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float

    @classmethod
    def from_array(cls, arr):
        return cls(*arr)


@dataclass
class PriceWindow:
    pair: CurrencyPair
    ohlc: np.ndarray

    @property
    def price(self):
        return self.ohlc[-1, -1]

    def append(self, ohlc_row):
        for j in range(len(self.ohlc) - 1):
            self.ohlc[j] = self.ohlc[j + 1]
        self.ohlc[-1] = ohlc_row

    def __getitem__(self, i: int):
        return self.ohlc[i]

    def candle(self, i: int) -> Candle:
        return Candle.from_array(self.ohlc[i])


class TradeSide(Enum):
    BUY = 1
    SELL = -1


@dataclass
class ATrade:
    pair: CurrencyPair
    open_price: float
    stop_loss: float
    take_profit: float

    @property
    def prices(self):
        return self.open_price, self.stop_loss, self.take_profit

    def __post_init__(self):
        p, sl, tp = self.prices
        assert (sl < p < tp) or (sl > p > tp)

    @property
    def type(self) -> TradeSide:
        if self.stop_loss < self.open_price:
            return TradeSide.BUY
        else:
            return TradeSide.SELL


@dataclass
class TradeIntent(ATrade):
    pass


@dataclass
class Trade(ATrade):
    close_price: float = None

    @property
    def pips(self):
        assert self.close_price is not None

        return (self.close_price - self.open_price) / self.pair.pip

    def must_close(self, price: float):
        p, sl, tp = self.prices
        if self.type == TradeSide.BUY:
            if p < sl or p > tp:
                return True
        else:
            if p > sl or p < tp:
                return True
        return False

    def close(self, price: float):
        self.close_price = price
