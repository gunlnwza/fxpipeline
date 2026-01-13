import pytest
import pandas as pd


class Order:
    def __init__(self, side, entry_price, sl, tp):
        self.side = side  # "buy" or "sell"
        self.entry_price = entry_price
        self.sl = sl
        self.tp = tp

        self.filled = False
        self.closed = False
        self.exit_price = None

    def process_bar(self, open, high, low, close):
        if self.side == "buy":
            if not self.filled:
                if low <= self.entry_price <= high:
                    filled = True

            if self.filled and not self.closed:
                if low <= self.sl:
                    close(self.sl)
                elif high >= self.tp:
                    close(self.tp)
                    
        elif self.side == "sell":
            if not filled:
                if low <= self.entry <= high:
                    filled = True

            if filled and not self.closed:
                if high >= self.sl:
                    close(self.sl)
                elif low <= self.tp:
                    close(self.tp)


class Simulation:
    def __init__(self, ohlcv: pd.DataFrame):
        self.ohlcv = ohlcv

        self.open = ohlcv["open"].to_numpy()
        self.high = ohlcv["high"].to_numpy()
        self.low = ohlcv["low"].to_numpy()
        self.close = ohlcv["close"].to_numpy()
        self.volume = ohlcv["volume"].to_numpy()

        self.i = 0
        self.orders = []

    def open_buy(self, entry_price, sl, tp):
        """Convert to buy limit, or buy stop"""
        self.orders.append(Order("buy", entry_price, sl, tp))

    def open_sell(self, entry_price, sl, tp):
        """Convert to sell limit, or buy stop"""
        self.orders.append(Order("sell", entry_price, sl, tp))

    def next(self):
        if self.i >= len(self.ohlcv):
            return

        o = self.open[self.i]
        h = self.high[self.i]
        l = self.low[self.i]
        c = self.close[self.i]
        for order in self.orders:
            if order.is_closed:
                continue
            order.process_bar(o, h, l, c)

        self.i += 1
        

@pytest.fixture
def sim():
    ohlcv = pd.DataFrame(
        [
            # up 5
            [12,14,11,13,0],
            [13,15,12,14,0],
            [14,16,13,15,0],
            [15,17,14,16,0],
            [16,18,15,17,0],

            # volatile bar 1
            [17,22,12,17,0],

            # down 3
            [17,18,15,16,0],
            [16,17,14,15,0],
            [15,16,13,14,0],

            # volatile bar 2
            [14,19,9,14,0],

            # up 5
            [14,16,13,15,0],
            [15,17,14,16,0],
            [16,18,15,17,0],
            [17,19,16,18,0],
            [18,20,17,19,0],
        ],
        columns=["open", "high", "low", "close", "volume"]
    )
    return Simulation(ohlcv)


# buy, open
def test_buy_limit_open_on_close(sim):
    # price go down; close hit entry_price, assert is opened
    pass

def test_buy_limit_open_on_low(sim):
    # price go down; low, but not close, hit entry_price, assert is opened
    pass

def test_buy_stop_open_on_close(sim):
    # price go up; close hit entry_price, assert is opened
    pass

def test_buy_stop_open_on_high(sim):
    # price go up; high, but not close, hit entry_price, assert is opened
    pass


# buy, close
def test_buy_order_sl_on_close(sim):
    # opened buy order; close hit sl, assert is closed
    pass

def test_buy_order_tp_on_close(sim):
    # opened buy order; close hit tp, assert is closed
    pass

def test_buy_order_sl_on_low(sim):
    # opened buy order; low, but not close, hit sl, assert is closed
    pass

def test_buy_order_tp_on_high(sim):
    # opened buy order; high, but not close, hit tp, assert is closed
    pass


# sell, open
def test_sell_limit_open_on_close(sim):
    # price go up; close hit entry_price, assert is opened
    pass

def test_sell_limit_open_on_high(sim):
    # price go up; high, but not close, hit entry_price, assert is opened
    pass

def test_sell_stop_open_on_close(sim):
    # price go up; close hit entry_price, assert is opened
    pass

def test_sell_stop_open_on_low(sim):
    # price go up; low, but not close, hit entry_price, assert is opened
    pass


# sell, close
def test_sell_order_sl_on_close(sim):
    # opened sell order; close hit sl, assert is closed
    pass

def test_sell_order_tp_on_close(sim):
    # opened sell order; close hit tp, assert is closed
    pass

def test_sell_order_sl_on_high(sim):
    # opened sell order; high, but not close, hit sl, assert is closed
    pass

def test_sell_order_tp_on_low(sim):
    # opened sell order; low, but not close, hit tp, assert is closed
    pass


# edge cases
def test_buy_sl_on_both_tp_and_sl(sim):
    pass

def test_sell_sl_on_both_tp_and_sl(sim):
    pass

def test_buy_same_bar_open_then_close(sim):
    pass

def test_sell_same_bar_open_then_close(sim):
    pass
