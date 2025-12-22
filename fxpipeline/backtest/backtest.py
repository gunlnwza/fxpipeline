import pandas as pd

from .strategy import Strategy
from ..core import Data, Trade, TradeIntent, CandlesWindow


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
        self.window = CandlesWindow(
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
        df = self.data.price.df
        for timestamp, row in df.iloc[self.bars:].iterrows():
            print(self.window.ohlc)
            self.manage_trade()
            print()
            self.window.append(row)

        if self.trade:
            self.close_trade()
