from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .order import Order

if TYPE_CHECKING:
    from .price import PricePoint


class AccountStatistics:
    def __init__(self):
        self.closed_orders: list[Order] = []
        # TODO: Equity curve
        # TODO: Balance curve

    def to_dict(self) -> dict:
        return {
            "orders": self.closed_orders,
            "trades": len(self.closed_orders),
            "pnl": sum(o.realized_pnl() for o in self.closed_orders)
        }

    def update(self, order: Order):
        self.closed_orders.append(order)


class Account:
    def __init__(self, balance):
        self.balance = balance
        self.order: Optional[Order] = None 

        self.stats = AccountStatistics()

    def __repr__(self) -> str:
        return f"Account({self.balance}, {self.order})"

    def equity(self, point: PricePoint):
        if not self.order:
            return self.balance
        return self.balance + self.order.current_pnl(point)

    # --- interfaces for Strategy
    def buy(self, point: PricePoint):
        if self.order is None:
            self.order = Order("buy", point)

    def sell(self, point: PricePoint):
        raise NotImplementedError

    def close(self, point: PricePoint):
        if self.order:
            pnl = self.order.close(point)
            self.stats.update(self.order)
            self.balance += pnl
            self.order = None
