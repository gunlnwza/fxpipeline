from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import pandas as pd


class Order:
    def __init__(self, type: str, i: int, price: float):
        self._type = type.lower()
        assert self._type in ("buy", "sell")

        self._open_i = i
        self._open_price = price

        self._close_i = None
        self._close_price = None

    def get_info(self) -> dict:
        return {
            "type": self._type,
            "open_i": self._open_i, "open_price": self._open_price,
            "close_i": self._close_i, "close_price": self._close_price
        }

    def close(self, i, price):
        self._close_i = i
        self._close_price = price

    @property
    def profit(self):
        return self.current_profit(self._close_price)

    def current_profit(self, price):
        price_diff = price - self._open_price
        if self._type == "sell":
            price_diff *= -1
        return price_diff


class Data:
    def __init__(self, df: pd.DataFrame, obs_size: int):
        # training/testing data
        self._df = df
        self._closes = df['close'].to_numpy()
        self._obs_size = obs_size

        # states
        self._i: int = self._obs_size  # window is [i - obs_size, i)
        self.order: Optional[Order] = None

        # info + log
        self.total_profit = 0

    def get_observation(self):
        closes = self._closes[self._i - self._obs_size:self._i]
        closes = (closes - closes.mean()) / closes.std()
        return closes

    def get_info(self):
        closes = self._closes[self._i - self._obs_size:self._i]

        info = {
            "i": self._i,
            "closes": closes,
            "total_profit": self.total_profit
        }
        if self.order:
            info["order"] = self.order.get_info()

        return info

    def step(self):
        if not self.is_truncated():
            self._i += 1

    def reset(self):
        self._i = self._obs_size
        self.order = None

    def is_terminated(self):
        return False

    def is_truncated(self):
        return self._i >= len(self._df)

    @property
    def current_price(self):
        return self._closes[self._i - 1]

    def buy(self):
        assert self.order is None
        self.order = Order("buy", self._i, self.current_price)

    def sell(self):
        assert self.order is None
        self.order = Order("sell", self._i, self.current_price)

    def close_order(self):
        assert self.order

        self.order.close(self._i, self.current_price)
        profit = self.order.profit
        self.order = None

        self.total_profit += profit

        return profit

    def current_profit(self):
        assert self.order
        return self.order.current_profit(self.current_price)
