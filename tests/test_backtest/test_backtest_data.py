import numpy as np
import pandas as pd
import pytest

from fxpipeline.backtest.backtest_data import Order, BacktestData


# --- Order

@pytest.fixture
def buy() -> Order:
    return Order("buy", 0, 21)


@pytest.fixture
def sell() -> Order:
    return Order("sell", 0, 21)


def test_init(buy):
    assert buy._open_i == 0
    assert buy._open_price == 21
    assert buy._close_i is None
    assert buy._close_price is None


def test_repr(buy):
    assert buy.__repr__() == "Order(buy, (0, 21), (None, None))"


def test_eq(buy, sell):
    assert (buy == sell) is False
    with pytest.raises(NotImplementedError):
        buy == 42


def test_current_profit(buy, sell):
    assert buy.current_profit(42) == 21
    assert sell.current_profit(42) == -21


def test_close(buy):
    buy.close(1, 42)
    assert buy._close_i == 1
    assert buy._close_price == 42


def test_get_info(buy):
    info = buy.get_info()
    assert set(info.keys()) == {"type", "close_i", "close_price", "open_i", "open_price"}
    assert info["type"] == "buy"
    assert info["open_i"] == 0
    assert info["open_price"] == 21
    assert info["close_i"] is None
    assert info["close_price"] is None


# --- Data

@pytest.fixture
def data() -> BacktestData:
    df_ohlc = pd.DataFrame({
        "open":  [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        "high":  [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "low":   [0,   1,  2,  3,  4,  5,  6,  7,  8,  9],
        "close": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    })
    return BacktestData(df_ohlc, obs_size=5)


def test_get_observation(data):
    observation = data.get_observation()
    expected_obs = np.array([
        [10, 30, 0, 20],
        [11, 31, 1, 21],
        [12, 32, 2, 22],
        [13, 33, 3, 23],
        [14, 34, 4, 24],
    ], dtype=np.float32)
    np.testing.assert_array_equal(observation, expected_obs)


def test_step(data):
    data.step()

    observation = data.get_observation()
    expected_obs = np.array([
        [11, 31, 1, 21],
        [12, 32, 2, 22],
        [13, 33, 3, 23],
        [14, 34, 4, 24],
        [15, 35, 5, 25]
    ], dtype=np.float32)
    np.testing.assert_array_equal(observation, expected_obs)


def test_reset(data):
    data.buy()

    data.reset()

    observation = data.get_observation()
    expected_obs = np.array([
        [10, 30, 0, 20],
        [11, 31, 1, 21],
        [12, 32, 2, 22],
        [13, 33, 3, 23],
        [14, 34, 4, 24],
    ], dtype=np.float32)
    np.testing.assert_array_equal(observation, expected_obs)

    assert data.order is None


def test_is_done_check(data):
    data.reset()

    for i in range(4):
        data.step()
        assert not data.terminated and not data.truncated

    data.step()  # truncated at the 5th time
    assert not data.terminated and data.truncated


def test_buy_order(data):
    data.reset()

    data.buy()
    assert data.order == Order("buy", 5, 24)
    assert data.current_profit() == 0

    data.step()

    profit = data.close_order()
    assert profit == 1
    assert data.order is None


def test_sell_order(data):
    data.reset()

    data.sell()
    assert data.order == Order("sell", 5, 24)
    assert data.current_profit() == 0

    data.step()

    profit = data.close_order()
    assert profit == -1
    assert data.order is None
