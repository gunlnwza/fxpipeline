from abc import ABC, abstractmethod
import numpy as np
import pprint


# class Order:
#     def __init__(self):
#         pass

class Account:
    def __init__(self, balance):
        self.balance = balance
        # TODO: make Order class
        self.order = None  # (just the open price for now)

        # primary stats
        # TODO: combine stats
        # self.stats = {
        #     "closed_orders": {},
        #     "trades": 0,
        #     "pnl": 0,
        # }
        self.closed_orders = {}  # time: price
        self.trades = 0
        self.pnl = 0

    def __repr__(self):
        return f"Account({self.balance}, {self.order})"

    def equity(self, price):
        if not self.order:
            return self.balance
        return self.balance + (self.order - price)  # TODO: use order.pnl()

    # --- interfaces for Strategy
    def buy(self, price):
        if self.order is None:
            self.order = price  # TODO

    # TODO: implement sell

    def close(self, price, i):
        if self.order:
            # pnl = self.order.close(price) #TODO set order flag as closed
            pnl = price - self.order
            self.balance += pnl
            self.order = None

            self.trades += 1  # TODO: stats
            self.pnl += pnl
            self.closed_orders[i] = price


class Strategy(ABC):
    @abstractmethod
    def act(self, account, prices: np.array):  # hopefully view won't slow down hot loop
        pass

class RandomAction(Strategy):
    def act(self, account: Account, prices: np.array, i):
        if not account.order:
            if np.random.random() < 0.5:
                account.buy(prices[-1])  # clearly need a np.array wrapper that expose current price, maybe a tiny pd.DataFrame design?
        else:
            if np.random.random() < 0.1:
                account.close(prices[-1], i)
    

class Simulation:
    def __init__(self, data: np.array, strategy: Strategy):
        self.data = data  # TODO: make data good, support index and time
        self.strategy = strategy
        self.summary = None

    def run(self):
        account = Account(100)

        for i in range(1, len(self.data)):
            if account.equity(self.data[i]) <= 0:
                break
            print(i, account)  # TODO: improve logging
            self.strategy.act(account, self.data[:i], i)

        if account.order:
            account.close(self.data[-1], len(self.data))

        # using dict is ok, every ML libs do it.
        # represent ground truth, derive meaningful ratios and features separately
        # or maybe just put common ratios in? maybe no
        self.summary = {
            "balance": account.balance,
            "trades": account.trades,
            "pnl": account.pnl,
            "orders": account.closed_orders.items()
        } 

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

    sim = Simulation(data, strategy)
    sim.run()
    pprint.pprint(sim.summary)

    sum = sim.summary
    orders = dict(sum["orders"])
    # print(order)
    plt.title("Backtest Result")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.plot(data)
    plt.scatter(orders.keys(), orders.values(), marker="^", color="green")
    plt.show()
