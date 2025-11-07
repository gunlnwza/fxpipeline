import numpy as np
import pandas as pd

from fxpipeline.backtest.data import Data, Order

df_ohlc = pd.DataFrame({
    "open":  [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "high":  [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
    "low":   [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
    "close": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
})
obs_size = 5
data = Data(df_ohlc, obs_size)


def test_get_observation():
    observation = data.get_observation()
    expected_obs = np.array([
        [10, 30, 0, 20],
        [11, 31, 1, 21],
        [12, 32, 2, 22],
        [13, 33, 3, 23],
        [14, 34, 4, 24],
    ], dtype=np.float32)
    np.testing.assert_array_equal(observation, expected_obs)


def test_get_info():
    info = data.get_info()
    assert isinstance(info, dict)


def test_step():
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


def test_reset():
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


def test_is_done_check():
    data.reset()

    for i in range(4):
        data.step()
        assert not data.terminated and not data.truncated

    data.step()  # truncated at the 5th time
    assert not data.terminated and data.truncated


def test_buy_order():
    data.reset()

    data.buy()
    assert data.order == Order("buy", 5, 24)
    assert data.current_profit() == 0

    data.step()

    profit = data.close_order()
    assert profit == 1
    assert data.order is None


def test_sell_order():
    data.reset()

    data.sell()
    assert data.order == Order("sell", 5, 24)
    assert data.current_profit() == 0

    data.step()

    profit = data.close_order()
    assert profit == -1
    assert data.order is None
