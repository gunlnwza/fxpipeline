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

        # TODO: polish, make it accurate
        w = self.window
        self.trade = Trade(w.pair, w.price, i.stop_loss, i.take_profit)
        print("> open_trade")

    def close_trade(self):
        assert self.trade

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
            self.window.append(row)
            print()


if __name__ == "__main__":
    random.seed(42)

    df = pd.DataFrame([
        [1, 1, 1, 1],
        [2, 2, 2, 2],
        [3, 3, 3, 3],
        [4, 4, 4, 4], 
        [5, 5, 5, 5],
        [6, 6, 6, 6],
        [7, 7, 7, 7],
        [8, 8, 8, 8],
        [9, 9, 9, 9],
        [10, 10, 10, 10]
    ])
    d = Data(ForexPrice(CurrencyPair("ABC", "DEF", pip=0.0001), "mock", df))
    st = Strategy()

    bt = Backtester(d, st)
    bt.run()
    print("[ Backtest Result ]")
    print("Pips:", bt.pips)
