from __future__ import annotations

import numpy as np

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

    def __repr__(self):
        return f"Order({self._type}, ({self._open_i}, {self._open_price})" \
            f", ({self._close_i}, {self._close_price}))"

    def __eq__(self, other: "Order"):
        if not isinstance(other, Order):
            raise NotImplementedError
        return self._type == other._type \
            and self._open_i == other._open_i and self._open_price == other._open_price \
            and self._close_i == other._close_i and self._close_price == other._close_price

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


class BacktestData:
    def __init__(self, df: pd.DataFrame, obs_size: int):
        assert "close" in df

        self._df = df
        self._arr = np.array(df)  # numpy array copy of df
        self._obs_size = obs_size
        self._i: int = obs_size  # window is [i - obs_size, i)

        self.order: Optional[Order] = None

        # info + log
        self.total_profit = 0

    def get_observation(self):
        return self._arr[self._i - self._obs_size:self._i]

    def get_info(self):
        info = {
            "i": self._i,
            "total_profit": self.total_profit
        }
        if self.order:
            info["order"] = self.order.get_info()
        return info

    def step(self):
        assert not self.terminated and not self.truncated
        self._i += 1

    def reset(self):
        self._i = self._obs_size
        self.order = None

    @property
    def terminated(self):
        return False

    @property
    def truncated(self):
        return self._i >= len(self._df)

    @property
    def current_price(self):
        return self._df.loc[self._i - 1, "close"]

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
