from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .price import PricePoint


# TODO: implement lot size and pips math

class Order:
    def __init__(self, type_: str, point: PricePoint):
        self.type = type_
        self.open_point = point
        self.close_point: Optional[PricePoint] = None

    def __repr__(self) -> str:
        return f"Order({self.type}, {self.open_point} to {self.close_point})"

    def current_pnl(self, point: PricePoint) -> float:
        if self.close_point:
            raise ValueError("order is closed, this function is forbidden")
        return point.price - self.open_point.price

    def realized_pnl(self) -> float:
        if not self.close_point:
            raise ValueError("order is not closed, so it does not have close_point")
        return self.close_point.price - self.open_point.price

    def close(self, point: PricePoint) -> float:
        self.close_point = point
        return self.realized_pnl()
