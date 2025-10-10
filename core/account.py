import pandas as pd

from .order import Order
from .price_point import PricePoint
from .action import BuyAction, SellAction


class AccountView:
    pass


# TODO: make histories neater, likely need to group them
# TODO: derive summaries from history
class Account:
    def __init__(self, balance: int):
        self.initial_balance = balance

        self.balance = balance  # realized returns
        self.equity = balance  # change with orders' position
        self.order = None  # remember where self buy/sell

        self.balance_history: list[float] = []
        self.equity_history: list[float] = []
        self.order_history: list[Order] = []

        # self.view = AccountView

        # summary examples
        #  peak = np.maximum.accumulate(equity_curve)
        #  drawdown = (equity_curve - peak) / peak
        #  max_drawdown = np.min(drawdown)

        #  daily_returns = np.diff(np.log(equity_curve))
        #  volatility = np.std(daily_returns) * np.sqrt(252)

    # METHODS MUST BE CALLED BY SIMULATOR ONLY
    # Only some attributes may be read by strategy
    def buy(self, cur: PricePoint, action: BuyAction):
        assert self.order is None
        self.order = Order("buy", action.size, action.ticker, cur)

    def sell(self, cur: PricePoint, action: SellAction):
        assert self.order is None
        self.order = Order("sell", action.size, action.ticker, cur)

    def close(self, cur: PricePoint):
        """do nothing if no order is opened"""
        if self.order is None:
            return
        self.order.close(cur)
        self.balance += self.order.pnl()
        self.order_history.append(self.order)
        self.order = None

    def update(self, cur: PricePoint):
        self.balance_history.append(self.balance)

        self.equity = self.balance
        if self.order:
            self.equity += self.order.pnl(cur)
        self.equity_history.append(self.equity)

    def order_history_df(self) -> pd.DataFrame:
        data = {"type": [], "open_time": [], "open_price": [],
                "close_time": [], "close_price": [], "pnl": []}
        for order in self.order_history:
            data["type"].append(order.type)
            data["open_time"].append(order.open_point.time)
            data["open_price"].append(order.open_point.price)
            data["close_time"].append(order.close_point.time)
            data["close_price"].append(order.close_point.price)
            data["pnl"].append(order.pnl())
        return pd.DataFrame(data)
