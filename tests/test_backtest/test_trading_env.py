import numpy as np
import pandas as pd
import pytest

from gymnasium import spaces

from fxpipeline.backtest import TradingEnv

"""
NOTE: does not test rendering-related features
"""

rng = np.random.default_rng(seed=42)

df = pd.DataFrame({
    "close": rng.random(10)

})
env = TradingEnv(df, obs_size=5, render_mode=None)


def test_action_space():
    assert env.action_space == spaces.Discrete(3, start=-1)


def test_observation_space():
    """Must infer shape from passed df"""
    pass


def test_get_observation():
    pass


def test_get_info():
    pass


def test_step():
    pass


def test_reset():
    pass
