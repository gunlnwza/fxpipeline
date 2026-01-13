import pandas as pd

from .error import EndOfSimulation
from .order import Order


class Simulation:
    def __init__(self, ohlcv: pd.DataFrame):
        self.ohlcv = ohlcv

        self.i = 0
        self.orders: list[Order] = []

        self.close_reason = ""

    def open_buy(self, entry_price, sl, tp):
        """Convert to buy limit, or buy stop"""
        self.orders.append(Order("buy", entry_price, sl, tp))

    def open_sell(self, entry_price, sl, tp):
        """Convert to sell limit, or buy stop"""
        self.orders.append(Order("sell", entry_price, sl, tp))

    @property
    def terminated(self):
        """Finish at the last bar of the df"""
        return self.i >= len(self.ohlcv) - 1

    def next(self):
        if self.terminated:
            raise EndOfSimulation

        self.i += 1

        row = self.ohlcv.iloc[self.i]
        o = row["open"]
        h = row["high"]
        l = row["low"]
        c = row["close"]
        for order in self.orders:
            if order.closed:
                continue
            order.process_bar(o, h, l, c)
