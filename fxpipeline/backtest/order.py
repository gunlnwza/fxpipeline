from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .price import PricePoint
    from ..core import CurrencyPair


class Order:
    def __init__(self, type_: str, lot: float, pair: CurrencyPair, point: PricePoint):
        self.type = type_
        self.lot = lot
        self.pair = pair
        self.open_point = point
        self.close_point: Optional[PricePoint] = None

    def __repr__(self) -> str:
        return f"Order({self.type}, {self.lot}, {self.pair}, {self.open_point} to {self.close_point})"

    def _pnl(self, point: PricePoint) -> float:
        # TODO: make correct
        price_diff = point.price - self.open_point.price
        # pips_diff = price_diff * pow(10, self.pair.pip_digits)
        
        pnl = price_diff
        pnl *= self.lot

        if self.type == "sell":
            pnl *= -1
        return pnl

    def current_pnl(self, point: PricePoint) -> float:
        if self.close_point:
            raise ValueError("order is closed, and return is already realized")
        return self._pnl(point)

    def realized_pnl(self) -> float:
        if not self.close_point:
            raise ValueError("order is not closed, return is not realized yet")
        return self._pnl(self.close_point)

    def close(self, point: PricePoint):
        self.close_point = point
