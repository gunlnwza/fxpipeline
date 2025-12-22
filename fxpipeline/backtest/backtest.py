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
            ohlcv=data.price.df.iloc[:self.bars].to_numpy()
        )
        self.trade = None

        # Metrics
        self._pips_list = []
        self.pips = 0

    def open_trade(self, intent: TradeIntent):
        assert self.trade is None
        assert intent is not None

        # TODO: polish, make it accurate, implement buy stop/sell stop?
        # w = self.window
        i = intent
        t = Trade(i.pair, i.open_price, i.stop_loss, i.take_profit)
        self.trade = t

    def close_trade(self):
        assert self.trade is not None

        t = self.trade
        t.close(self.window.price)
        self.pips += t.pips
        self.trade = None

    def manage_trade(self):
        if not self.trade:
            intent = self.strategy.get_intent(self.window)
            if intent:
                self.open_trade(intent)
        else:
            if self.trade.must_close(self.window.price):
                self.close_trade()

    def run(self):
        df = self.data.price.df
        for i, t_ohlcv in enumerate(df.iloc[self.bars:].iterrows()):
            _, ohlcv = t_ohlcv
            self.manage_trade()

            self.window.append(ohlcv)
            self._pips_list.append(self.pips)

        if self.trade:
            self.close_trade()
        self._pips_list.append(self.pips)
