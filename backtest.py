from abc import ABC, abstractmethod
import numpy as np
import pprint
from typing import Optional


class Order:
    def __init__(self, type_: str, current_price: float, i):
        self.type = type_
        self.open_price = current_price  # TODO: add PricePoint
        self.open_index = i
        self.close_price = None
        self.close_index = None

    def __repr__(self):
        return f"Order({self.type} {self.open_price:.2f} {self.close_price:.2f})"

    def pnl(self, current_price: float) -> float:  # TODO: I hate this name btw
        return current_price - self.open_price

    @property
    def money_made(self) -> float:
        # TODO: handle sell
        return self.close_price - self.open_price

    def close(self, current_price: float, i) -> float:
        self.close_price = current_price
        self.close_index = i
        return self.money_made


class AccountStatistics:
    def __init__(self):
        self.closed_orders = []
        self.trades = 0
        self.pnl = 0
        # Equity curve
        # Balance curve

    def to_dict(self) -> dict:
        return {
            "orders": self.closed_orders,
            "trades": self.trades,
            "pnl": self.pnl
        }

    def update(self, order: Order):
        self.closed_orders.append(order)
        self.trades += 1
        self.pnl += order.money_made


class Account:
    def __init__(self, balance):
        self.balance = balance
        self.order: Optional[Order] = None 

        self.stats = AccountStatistics()

    def __repr__(self) -> str:
        return f"Account({self.balance}, {self.order})"

    def equity(self, current_price: float):
        if not self.order:
            return self.balance
        return self.balance + self.order.pnl(current_price)

    # --- interfaces for Strategy
    def buy(self, current_price: float, i):
        if self.order is None:
            self.order = Order("buy", current_price, i)

    def sell(self, current_price: float):
        raise NotImplementedError

    def close(self, current_price: float, i):
        if self.order:
            pnl = self.order.close(current_price, i)
            self.balance += pnl
            self.stats.update(self.order)
            self.order = None


class Strategy(ABC):
    @abstractmethod
    def act(self, account, prices: np.array):  # hopefully view won't slow down hot loop
        pass


class RandomAction(Strategy):
    def act(self, account: Account, prices: np.array, i):
        if not account.order:
            if np.random.random() < 0.5:
                account.buy(prices[-1], i)  # clearly need a np.array wrapper that expose current price, maybe a tiny pd.DataFrame design?
        else:
            if np.random.random() < 0.1:
                account.close(prices[-1], i)
    

class Simulation:
    def __init__(self, data: np.array, strategy: Strategy, account: Account):
        self.data = data  # TODO: make data good, support index and time
        self.strategy = strategy
        self.summary = None
        self.account = account

    def run(self):
        for i in range(1, len(self.data)):
            if self.account.equity(self.data[i]) <= 0:
                break
            self.strategy.act(self.account, self.data[:i], i)

        if self.account.order:
            self.account.close(self.data[-1], i)

        # using dict is ok, every ML libs do it.
        # represent ground truth, derive meaningful ratios and features separately
        # or maybe just put common ratios in? maybe no
        self.summary = {"account": self.account.stats.to_dict()} 

"""
# sklearn
model.get_params() → dict
grid_search.cv_results_ → dict
classification_report() → dict

# tf, keras
model.evaluate() → list or dict
tf.summary.scalar(...) → basically dict-backed logging
history.history → dict of metrics

# pd
df.describe().to_dict()
groupby().agg().to_dict()
"""

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    data = np.full(100, 42) + np.random.normal(0.1, 1, 100).cumsum()
    strategy = RandomAction()
    account = Account(100)

    sim = Simulation(data, strategy, account)
    sim.run()
    pprint.pprint(sim.summary)

    sum = sim.summary
    orders: list[Order] = sum["account"]["orders"]
    plt.title("Backtest Result")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.plot(data)
    for o in orders:
        plt.plot([o.open_index, o.close_index], [o.open_price, o.close_price], color="green", lw=2, ls="--", ms=5, marker="o",)
    plt.show()
