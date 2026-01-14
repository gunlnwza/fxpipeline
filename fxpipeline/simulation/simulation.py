import pandas as pd

from .error import EndOfSimulation
from .order import Order


class Simulation:
    def __init__(self, ohlcv: pd.DataFrame, ticker: str = "", pip_digits: int = 4):
        self.ohlcv = ohlcv
        self.ticker = ticker
        self.pip_digits = pip_digits

        self.i = 0
        self.orders: list[Order] = []
        self.pips_counted: list[bool] = []

        self.win_pips = 0
        self.loss_pips = 0

    def __repr__(self) -> str:
        return f"Simulation({self.ticker}, {self.pip_digits}, {self.i})"

    def open_buy(self, entry_price, sl, tp):
        """Convert to buy limit, or buy stop"""
        self.orders.append(Order("buy", entry_price, sl, tp))
        self.pips_counted.append(False)

    def open_sell(self, entry_price, sl, tp):
        """Convert to sell limit, or buy stop"""
        self.orders.append(Order("sell", entry_price, sl, tp))
        self.pips_counted.append(False)

    @property
    def terminated(self):
        """Finish at the last bar of the df"""
        return self.i >= len(self.ohlcv) - 1
    
    @property
    def current_ohlcv(self):
        return self.ohlcv.iloc[self.i]

    @property
    def price(self):
        return self.ohlcv.iloc[self.i]["close"]

    def _count_pips_if_not_counted(self, i: int, order: Order):
        if self.pips_counted[i]:
            return
        if order.price_diff > 0:
            self.win_pips += round(order.price_diff * pow(10, self.pip_digits))
        else:
            self.loss_pips += round(-order.price_diff * pow(10, self.pip_digits))
        self.pips_counted[i] = True

    def next(self):
        if self.terminated:
            raise EndOfSimulation

        self.i += 1

        row = self.ohlcv.iloc[self.i]
        o = row["open"]
        h = row["high"]
        l = row["low"]
        c = row["close"]
        for i, order in enumerate(self.orders):
            if order.closed:
                self._count_pips_if_not_counted(i, order)
                continue
            order.process_bar(o, h, l, c)
