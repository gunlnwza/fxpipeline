import numpy as np
import pandas as pd

import gymnasium as gym
from gymnasium import spaces


class TradingEnv(gym.Env):
    def __init__(self, ticker: str, obs_size=10, lookahead_size=100):
        super().__init__()

        self._obs_size = obs_size
        self._lookahead_size = lookahead_size
        
        # --- Load data
        self.df = pd.read_csv(f"{ticker}.csv", parse_dates=True, index_col="timestamp")
    
        self.prices = self.df["close"].values
        self.fast_ma = self.df["close"].rolling(20).mean().values
        self.slow_ma = self.df["close"].rolling(50).mean().values
        self.ma_diff = self.fast_ma - self.slow_ma

        # --- Environment state
        self._row_index = obs_size

        # --- Observation & action spaces
        self.observation_space = spaces.Box(-np.inf, np.inf, (3, obs_size), np.float32)
        # self.observation_space = spaces.Box(-np.inf, np.inf, (obs_size,), np.float32)
    
        self.action_space = spaces.Discrete(2)  # 0 = Hold, 1 = Buy
    
    def _get_observation(self):
        # prices = self.prices[self._row_index - self._obs_size : self._row_index]
        # prices = (prices - prices.mean()) / prices.std()

        fast_ma = self.fast_ma[self._row_index - self._obs_size : self._row_index]
        fast_ma = (fast_ma - fast_ma.mean()) / fast_ma.std()

        slow_ma = self.slow_ma[self._row_index - self._obs_size : self._row_index]
        slow_ma = (slow_ma - slow_ma.mean()) / slow_ma.std()

        ma_diff = self.ma_diff[self._row_index - self._obs_size : self._row_index]
        ma_diff = (ma_diff - ma_diff.mean()) / ma_diff.std()

        # window = np.array([prices, fast_ma, slow_ma], np.float32)
        window = ma_diff
        window = np.array([fast_ma, slow_ma, ma_diff], np.float32)
        return window

    def reset(self, seed=None):
        self._row_index = self._obs_size
        return self._get_observation(), {}

    def step(self, action):
        obs = self._get_observation()

        current_price = self.prices[self._row_index - 1]
        future_prices = self.prices[self._row_index : min(self._row_index + self._lookahead_size, len(self.prices))]

        reward = 0
        if action == 1:
            diff = future_prices - current_price
            returns = np.sum(diff)  # ++ when up, ~0 in volatile, -- when down
            max_possible_pnl = np.max(diff)
            min_possible_pnl = np.min(diff)

            reward = returns + max_possible_pnl + min_possible_pnl * 10

        # --- Advance time
        done = False
        self._row_index += 1
        if self._row_index >= len(self.prices):
            done = True

        return obs, reward, done, False, {}

    def render(self):
        print(f"t={self._row_index}, pos={self.position}, price={self.prices[self._row_index-1]:.2f}")
