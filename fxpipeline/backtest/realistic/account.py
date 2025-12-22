from .order import Order, BuyOrder, SellOrder

from ..base import PricePoint

RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


class Account:
    MAX_ORDERS = 10  # Having 10 simultaneous orders is already a generous assumption

    def __init__(self, balance=1000):
        self.balance = balance
        self.equity = balance
        self.orders: list[Order] = []

        self.balance_arr = []
        self.equity_arr = []
        self.closed_orders: list[Order] = []

    def __repr__(self):
        return (
            "Account("
            f"balance={self.balance:.2f}, "
            f"equity={self.equity:.2f}, "
            f"orders={len(self.orders)}"
            ")"
        )

    def _close_position(self, o: Order, point: PricePoint):
        o.close_position(point)
        self.balance += o.profit
        self.orders.remove(o)
        self.closed_orders.append(o)

    def update(self, point: PricePoint):
        for o in self.orders:
            if o.must_close(point):
                self._close_position(o, point)
        self.equity = self.balance + sum(
            o.unrealized_profit(point) for o in self.orders
        )

        self.balance_arr.append(self.balance)
        self.equity_arr.append(self.equity)

    def summarize(self, point: PricePoint):
        """Close all orders"""
        for o in self.orders.copy():
            self._close_position(o, point)

    def buy(self, point: PricePoint, size: float = 0.01):
        if len(self.orders) >= self.MAX_ORDERS:
            print(f"{YELLOW}Tried to buy when max order{RESET}")
            return
        self.orders.append(BuyOrder(point, size))

    def sell(self, point: PricePoint, size: float = 0.01):
        if len(self.orders) >= self.MAX_ORDERS:
            print(f"{YELLOW}Tried to sell when max order{RESET}")
            return
        self.orders.append(SellOrder(point, size))

    def is_blown(self):
        if self.equity <= 0:
            print(f"{RED}Account blown{RESET}")
            return True
        return False
