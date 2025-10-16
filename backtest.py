from abc import ABC, abstractmethod
import numpy as np
import pprint
from typing import Optional

import matplotlib.pyplot as plt


class PricePoint:
    def __init__(self, index, price):
        self.index = index
        self.price = price


class Order:
    def __init__(self, type_: str, point: PricePoint):
        self.type = type_
        self.open_point = point
        self.close_point: Optional[PricePoint] = None

    def __repr__(self):
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


class Strategy(ABC):
    @abstractmethod
    def act(self, account, prices: np.array):  # hopefully view won't slow down hot loop
        pass

class RandomAction(Strategy):
    def act(self, account: Account, point: PricePoint):
        if not account.order:
            if np.random.random() < 0.5:
                account.buy(point)  # clearly need a np.array wrapper that expose current price, maybe a tiny pd.DataFrame design?
        else:
            if np.random.random() < 0.1:
                account.close(point)
    

class Simulation:
    def __init__(self, data: np.array, strategy: Strategy, account: Account):
        self.data = data  # TODO: make data good, support index and time
        self.strategy = strategy
        self.account = account

        self.summary = None

    def run(self):
        for i in range(1, len(self.data)):
            point = PricePoint(i, self.data[i])
            if self.account.equity(point) <= 0:
                break
            self.strategy.act(self.account, point)

        if self.account.order:
            self.account.close(point)

        self.summary = {"account": self.account.stats.to_dict()} 


def plot_result(summary: dict):
    orders: list[Order] = summary["account"]["orders"]
    plt.title("Backtest Result")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.plot(data)
    for o in orders:
        xs = [o.open_point.index, o.close_point.index]
        ys = [o.open_point.price, o.close_point.price]
        plt.plot(xs, ys, color="green", lw=2, ls="--", ms=5, marker="o",)
    plt.show()


if __name__ == "__main__":
    data = np.full(100, 42) + np.random.normal(0.1, 1, 100).cumsum()
    strategy = RandomAction()
    account = Account(100)

    simulation = Simulation(data, strategy, account)
    simulation.run()
    pprint.pprint(simulation.summary)
    plot_result(simulation.summary)
