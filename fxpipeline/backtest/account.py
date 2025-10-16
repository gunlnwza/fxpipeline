from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .order import Order

if TYPE_CHECKING:
    from .price import PricePoint


class AccountStatistics:
    def __init__(self, balance):
        self.closed_orders: list[Order] = []
        self.equity = [balance] #TODO
        self.balance = [balance] # TODO

    def to_dict(self) -> dict:
        orders = []
        for o in self.closed_orders:
            orders.append((
                o.open_point.index, o.close_point.index,
                o.open_point.price, o.close_point.price))
        return {
            "orders": orders,
            "equity": self.equity,
            "balance": self.balance,
            "trades": len(self.closed_orders),
            "pnl": sum(o.realized_pnl() for o in self.closed_orders)
        }

    # --- interfaces for Simulation
    # def update_equity_curve(self, point: PricePoint):
        # self.equity.append(self.equity[-1] + point.price)


class Account:
    def __init__(self, balance):
        self.stats = AccountStatistics(balance)

        self.balance = balance
        self.order: Optional[Order] = None 


    def __repr__(self) -> str:
        return f"Account({self.balance}, {self.order})"
    
    def equity(self, point: PricePoint):
        if self.order:
            return self.balance + self.order.current_pnl(point)
        else:
            return self.balance
        
    def update_curve(self):  # TODO
        pass

    # --- interfaces for Strategy
    def buy(self, point: PricePoint):
        if self.order is None:
            self.order = Order("buy", point)

    def sell(self, point: PricePoint):
        raise NotImplementedError

    def close(self, point: PricePoint):
        if self.order:
            pnl = self.order.close(point)
            self.balance += pnl
            self.stats.closed_orders.append(self.order)
            self.order = None
