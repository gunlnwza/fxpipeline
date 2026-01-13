import pytest
import pandas as pd


class EndOfSimulation(Exception):
    pass

class InvalidOrder(Exception):
    pass


class Order:
    def __init__(self, side, open_price, sl, tp):
        self.side = side  # "buy" or "sell"
        self.open_price = open_price
        self.sl = sl
        self.tp = tp

        self.opened = False
        self.closed = False
        self.close_price = None

        self.reason = None

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
                if low <= self.entry_price <= high:
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
        return self.i >= len(self.ohlcv)

    def next(self):
        if self.terminated:
            raise EndOfSimulation

        o = self.open[self.i]
        h = self.high[self.i]
        l = self.low[self.i]
        c = self.close[self.i]
        for order in self.orders:
            if order.closed:
                continue
            order.process_bar(o, h, l, c)

        self.i += 1


@pytest.fixture
def sim() -> Simulation:
    ohlcv = pd.DataFrame(
        [
            # up 5
            [12,13,12,13,0],
            [13,14,13,14,0],
            [14,15,14,15,0],
            [15,17,14,16,0],
            [16,18,15,17,0],

            # volatile bar 1
            [17,22,12,18,0],

            # down 5
            [18,18,17,17,0],
            [17,17,16,16,0],
            [16,16,15,15,0],
            [15,16,13,14,0],
            [14,15,12,13,0],

            # volatile bar 2
            [13,18,8,12,0],

            # up 5
            [12,13,12,13,0],
            [13,14,13,14,0],
            [14,15,14,15,0],
            [15,17,14,16,0],
            [16,18,15,17,0],
        ],
        columns=["open", "high", "low", "close", "volume"]
    )
    return Simulation(ohlcv)

@pytest.fixture
def right_before_first_volatile_bar(sim: Simulation) -> Simulation:
    for _ in range(4):
        sim.next()
    return sim

@pytest.fixture
def right_after_first_volatile_bar(right_before_first_volatile_bar: Simulation) -> Simulation:
    sim = right_before_first_volatile_bar
    sim.next()
    return sim


def assert_planned(order, side):
    assert order.side == side
    assert not order.opened
    assert not order.closed


def assert_opened(order, side):
    assert order.side == side
    assert order.opened
    assert not order.closed


def assert_closed(order, reason):
    assert order.opened
    assert order.closed
    assert order.close_reason == reason



def test_end_of_simulation(sim: Simulation):
    """raise error if simulation has already ended but call next()"""
    while not sim.terminated:
        sim.next()

    with pytest.raises(EndOfSimulation):
        sim.next()

# open buy
def test_bad_buy_sl(sim: Simulation):
    with pytest.raises(InvalidOrder, match="bad sl"):
        sim.open_buy(10, 11, 11)

def test_bad_buy_tp(sim: Simulation):
    with pytest.raises(InvalidOrder, match="bad tp"):
        sim.open_buy(10, 9, 9)

def test_buy_limit_open_on_close(right_after_first_volatile_bar: Simulation):
    """price go down; close hit entry_price, assert is opened"""
    sim = right_after_first_volatile_bar

    sim.open_buy(17.5, 0, 100)
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_opened(sim.orders[0], "buy")

def test_buy_limit_open_on_low(right_before_first_volatile_bar: Simulation):
    """price go down; low, but not close, hit entry_price, assert is opened"""
    sim = right_before_first_volatile_bar

    sim.open_buy(12, 0, 100)  # touch bottom wick
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_opened(sim.orders[0], "buy")

def test_buy_stop_open_on_close(sim: Simulation):
    """price go up; close hit entry_price, assert is opened"""
    sim.open_buy(13.5, 0, 100)
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_opened(sim.orders[0], "buy")

def test_buy_stop_open_on_high(right_before_first_volatile_bar: Simulation):
    """price go up; high, but not close, hit entry_price, assert is opened"""
    sim = right_before_first_volatile_bar

    sim.open_buy(22, 0, 100)  # touch top wick
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_opened(sim.orders[0], "buy")


# close buy
def test_buy_order_sl_on_close(right_after_first_volatile_bar: Simulation):
    """opened buy order; close hit sl, assert is closed"""
    sim = right_after_first_volatile_bar

    sim.open_buy(17.5, 16.5, 100)
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_opened(sim.orders[0], "buy")

    sim.next()
    assert_closed(sim.orders[0], "sl")

def test_buy_order_sl_on_low(right_after_first_volatile_bar: Simulation):
    """opened buy order; low, but not close, hit sl, assert is closed"""
    sim = right_after_first_volatile_bar

    sim.open_buy(17.5, 8, 100)
    assert_planned(sim.orders[0], "buy")

    sim.next()

    for _ in range(5):
        assert_opened(sim.orders[0], "buy")
        sim.next()
    assert_closed(sim.orders[0], "sl")

def test_buy_order_tp_on_close(sim: Simulation):
    """opened buy order; close hit tp, assert is closed"""
    sim.open_buy(13.5, 0, 14.5)
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_opened(sim.orders[0], "buy")
    
    sim.next()
    assert_closed(sim.orders[0], "tp")

def test_buy_order_tp_on_high(sim: Simulation):
    """opened buy order; high, but not close, hit tp, assert is closed"""
    sim.open_buy(13.5, 0, 22)
    assert_planned(sim.orders[0], "buy")

    sim.next()

    for _ in range(4):
        assert_opened(sim.orders[0], "buy")
        sim.next()
    assert_closed(sim.orders[0], "tp")


# open sell
def test_bad_sell_sl(sim: Simulation):
    with pytest.raises(InvalidOrder, match="bad sl"):
        sim.open_buy(10, 9, 9)

def test_bad_sell_tp(sim: Simulation):
    with pytest.raises(InvalidOrder, match="bad tp"):
        sim.open_buy(10, 11, 11)

def test_sell_limit_open_on_close(sim: Simulation):
    """price go up; close hit entry_price, assert is opened"""
    sim.open_sell(13.5, 0, 100)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_opened(sim.orders[0], "sell")


def test_sell_limit_open_on_high(right_before_first_volatile_bar: Simulation):
    """price go up; high, but not close, hit entry_price, assert is opened"""
    sim = right_before_first_volatile_bar

    sim.open_sell(22, 0, 100)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_opened(sim.orders[0], "sell")


def test_sell_stop_open_on_close(right_after_first_volatile_bar: Simulation):
    """price go down; close hit entry_price, assert is opened"""
    sim = right_after_first_volatile_bar

    sim.open_sell(17.5, 100, 0)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_opened(sim.orders[0], "sell")


def test_sell_stop_open_on_low(right_after_first_volatile_bar: Simulation):
    """price go down; low, but not close, hit entry_price, assert is opened"""
    sim = right_after_first_volatile_bar

    sim.open_sell(13.5, 100, 0)

    for _ in range(4):
        assert_planned(sim.orders[0], "sell")
        sim.next()
    assert_opened(sim.orders[0], "sell")


# close sell
def test_sell_order_sl_on_close(sim: Simulation):
    """opened sell order; close hit sl, assert is closed"""
    sim.open_sell(13.5, 14.5, 0)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_opened(sim.orders[0], "sell")

    sim.next()
    assert_closed(sim.orders, "sl")

def test_sell_order_sl_on_high(sim: Simulation):
    """opened sell order; high, but not close, hit sl, assert is closed"""
    sim.open_sell(13.5, 22, 0)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    for _ in range(4):
        assert_opened(sim.orders[0], "sell")
        sim.next()
    assert_closed(sim.orders[0], "sl")


def test_sell_order_tp_on_close(right_after_first_volatile_bar: Simulation):
    """opened sell order; close hit tp, assert is closed"""
    sim = right_after_first_volatile_bar

    sim.open_sell(17.5, 100, 16.5)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_opened(sim.orders[0], "sell")

    sim.next()
    assert_closed(sim.orders[0], "tp")


def test_sell_order_tp_on_low(right_after_first_volatile_bar: Simulation):
    """opened sell order; low, but not close, hit tp, assert is closed"""
    sim = right_after_first_volatile_bar

    sim.open_sell(17.5, 100, 16.5)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    for _ in range(5):
        assert_opened(sim.orders[0], "sell")
        sim.next()
    assert_closed(sim.orders[0], "tp")

# edge cases
def test_same_bar_buy_sl(right_before_first_volatile_bar: Simulation):
    sim = right_before_first_volatile_bar

    sim.open_buy(17.5, 16, 100)
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_closed(sim.orders[0], "sl")

def test_same_bar_buy_both_tp_and_sl(right_before_first_volatile_bar: Simulation):
    """high volatility bar; tp and sl are both engulfed by high and low, must sl"""
    sim = right_before_first_volatile_bar

    sim.open_buy(17.5, 16, 20)
    assert_planned(sim.orders[0], "buy")

    sim.next()
    assert_closed(sim.orders[0], "sl")


def test_same_var_sell_sl(right_before_first_volatile_bar: Simulation):
    sim = right_before_first_volatile_bar

    sim.open_sell(17.5, 20, 0)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_closed(sim.orders[0], "sl")


def test_same_bar_sell_both_tp_and_sl(right_before_first_volatile_bar: Simulation):
    """high volatility bar; tp and sl are both engulfed by low and high, must sl"""
    sim = right_before_first_volatile_bar

    sim.open_sell(17.5, 20, 16)
    assert_planned(sim.orders[0], "sell")

    sim.next()
    assert_closed(sim.orders[0], "sl")
