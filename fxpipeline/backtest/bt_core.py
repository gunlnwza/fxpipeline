from dataclasses import dataclass

import numpy as np

from ..core import CurrencyPair


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


@dataclass
class TradeIntent:
    pair: CurrencyPair
    open_price: float
    stop_loss: float
    take_profit: float


# Trade and TradeIntent should inherit from this
@dataclass
class ATrade:
    pair: CurrencyPair
    open_price: float
    stop_loss: float
    take_profit: float

    def type(self):  # should return enum
        assert self.stop_loss != self.open_price

        if self.stop_loss < self.open_price:
            return "buy"
        else:
            return "sell"

@dataclass
class Trade:
    pair: CurrencyPair
    open_price: float
    stop_loss: float
    take_profit: float
    close_price: float = None

    @property
    def pips(self):
        assert self.close_price
        return (self.close_price - self.open_price) / self.pair.pip

    def must_close(self, price: float):
        if price < self.stop_loss or price > self.take_profit:
            return True
        return False

    def close(self, price: float):
        self.close_price = price
