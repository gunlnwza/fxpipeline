from dataclasses import dataclass

from .data import Ticker
from .price_point import PricePoint


# TODO: check + learn pips maths

@dataclass
class Order:
    type: str
    size: float
    ticker: Ticker
    open_point: PricePoint
    close_point: PricePoint = None

    def close(self, cur: PricePoint):
        self.close_point = cur

    def pnl(self, cur: PricePoint = None) -> float:
        if cur is None:
            cur = self.close_point
        assert cur is not None

        # pip calculation
        if self.ticker.to_symbol == "JPY":
            pip = 0.01
        else:
            pip = 0.0001

        price_diff = cur.price - self.open_point.price
        if self.type == "sell":
            price_diff *= -1

        pip_value_per_lot = (pip * 100_000) / cur.price
        return price_diff / pip * pip_value_per_lot * self.size

    def pips(self, cir: PricePoint = None) -> float:
        raise NotImplementedError  # TODO[pips]: implement
