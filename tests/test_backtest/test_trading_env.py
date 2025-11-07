import numpy as np
import pandas as pd

from gymnasium import spaces

from fxpipeline.backtest import TradingEnv
from fxpipeline.backtest.data import Order

"""
NOTE: does not test rendering-related features
"""

df_ohlc = pd.DataFrame({
    "open":  [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],  # have 6 windows
    "high":  [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
    "low":   [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
    "close": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
})
df_close = pd.DataFrame({
    "close": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
})
obs_size = 5

env_ohlc = TradingEnv(df_ohlc, obs_size, render_mode=None)
env_close = TradingEnv(df_close, obs_size, render_mode=None)


def test_action_space():
    """{Buy, Hold, Sell} is already a good design decision"""
    assert env_ohlc.action_space == spaces.Discrete(3, start=-1)


def test_observation_space():
    """Must infer shape from passed df"""
    assert env_ohlc.observation_space == spaces.Box(-np.inf, np.inf, (4, obs_size), np.float32)
    assert env_close.observation_space == spaces.Box(-np.inf, np.inf, (1, obs_size), np.float32)


def test_reset():
    observation, info = env_ohlc.reset()
    assert isinstance(observation, np.ndarray)
    assert isinstance(info, dict)


def test_step():
    observation, reward, terminated, truncated, info = env_ohlc.step(0)
    assert isinstance(observation, np.ndarray)
    assert reward == 0
    assert terminated is False
    assert truncated is False
    assert isinstance(info, dict)


def test_buy():
    env_ohlc.reset()

    for _ in range(4):
        observation, reward, terminated, truncated, info = env_ohlc.step(1)
        assert truncated is False
        assert reward == 0

    observation, reward, terminated, truncated, info = env_ohlc.step(1)
    assert reward == 0  # do not force-liquidate
    assert truncated is True


def test_sell():
    env_ohlc.reset()

    for _ in range(4):
        observation, reward, terminated, truncated, info = env_ohlc.step(-1)
        assert truncated is False
        assert reward == 0

    observation, reward, terminated, truncated, info = env_ohlc.step(-1)
    assert reward == 0  # do not force-liquidate
    assert truncated is True


def test_open_then_close():
    # buy
    for action in (0, -1):
        env_ohlc.reset()

        observation, reward, terminated, truncated, info = env_ohlc.step(1)
        assert env_ohlc.data.order == Order("buy", 5, 24)
        assert reward == 0

        observation, reward, terminated, truncated, info = env_ohlc.step(action)
        assert env_ohlc.data.order is None
        assert reward == 1

    # sell
    for action in (0, 1):
        env_ohlc.reset()

        observation, reward, terminated, truncated, info = env_ohlc.step(-1)
        assert env_ohlc.data.order == Order("sell", 5, 24)
        assert reward == 0

        observation, reward, terminated, truncated, info = env_ohlc.step(action)
        assert env_ohlc.data.order is None
        assert reward == -1


def test_truncated():
    for _ in range(42):
        observation, reward, terminated, truncated, info = env_ohlc.step(0)
        if truncated:
            break
