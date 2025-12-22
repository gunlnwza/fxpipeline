from typing import Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from uuid import uuid4

from ..base import PricePoint


@dataclass(eq=False)
class Order(ABC):
    open: PricePoint
    size: float = 0.01
    sl: Optional[float] = None
    tp: Optional[float] = None
    close: Optional[PricePoint] = None
    _id: str = field(default_factory=lambda: uuid4().hex, init=False)

    def __hash__(self):
        return hash(self._id)

    @abstractmethod
    def _price_diff(self, a: PricePoint, b: PricePoint):
        pass

    def unrealized_profit(self, point: PricePoint):
        return self._price_diff(self.open, point) * self.size

    @property
    def profit(self):
        return self._price_diff(self.open, self.close) * self.size

    def must_close(self, point: PricePoint):
        if self.sl and self._price_diff(self.sl, point) < 0:
            return True
        if self.tp and self._price_diff(self.tp, point) > 0:
            return True
        return False

    def close_position(self, point: PricePoint):
        self.close = point


@dataclass(eq=False)
class BuyOrder(Order):
    def _price_diff(self, a: PricePoint, b: PricePoint):
        return b.price - a.price


@dataclass(eq=False)
class SellOrder(Order):
    def _price_diff(self, a: PricePoint, b: PricePoint):
        return a.price - b.price
