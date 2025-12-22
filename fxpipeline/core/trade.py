from dataclasses import dataclass
from enum import Enum

from ..core import CurrencyPair


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
