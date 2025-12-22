import random

import numpy as np
import pandas as pd

from .strategy import Strategy
from .bt_core import Trade, TradeIntent, PriceWindow  # TODO: merge with core/ later
from ..core import CurrencyPair, ForexPrice, Data


class Backtester:
    """
    ### Constraints
    - Show only latest 100 bars.
    - Only one trade at a time.
    """
    def __init__(self, data: Data, strategy: Strategy):
        # Config
        self.data = data
        self.strategy = strategy
        self.bars = 5  # mock with 5, real is 100 bars

        # State
        self.window = PriceWindow(
            pair=data.price.pair, 
            ohlc=data.price.df.iloc[:self.bars].to_numpy()
        )
        self.trade = None

        # Metrics
        self.pips = 0

    def open_trade(self, i: TradeIntent):
        assert self.trade is None

        # TODO: polish, make it accurate, implement buy stop/sell stop?
        w = self.window
        self.trade = Trade(w.pair, w.price, i.stop_loss, i.take_profit)
        print("> open_trade")

    def close_trade(self):
        assert self.trade is not None

        t = self.trade
        t.close(self.window.price)
        self.pips += t.pips
        print(f"> close_trade: made {t.pips} pips")
        self.trade = None

    def manage_trade(self):
        if not self.trade:
            intent = self.strategy.get_intent(self.window)
            self.open_trade(intent)
        else:
            if self.trade.must_close(self.window.price):
                self.close_trade()

    def run(self):
        for timestamp, row in df.iloc[self.bars:].iterrows():
            print(self.window.ohlc)
            self.manage_trade()
            print()
            self.window.append(row)

        if self.trade:
            self.close_trade()


if __name__ == "__main__":
    random.seed(42)

    df = pd.DataFrame([
        [1.5, 1.9, 1.1, 1.7],
        [2.5, 2.9, 2.1, 2.7],
        [3.5, 3.9, 3.1, 3.7],
        [4.5, 4.9, 4.1, 4.7], 
        [5.5, 5.9, 5.1, 5.7],
        [6.5, 6.9, 6.1, 6.7],
        [7.5, 7.9, 7.1, 7.7],
        [8.5, 8.9, 8.1, 8.7],
        [9.5, 9.9, 9.1, 9.7],
        [10.5, 10.9, 10.1, 10.7]
    ])

    d = Data(ForexPrice(CurrencyPair("ABC", "DEF", pip=0.0001), "mock", df))
    st = Strategy()

    bt = Backtester(d, st)
    bt.run()
    print("[ Backtest Result ]")
    print("Pips:", bt.pips)
