import numpy as np
import pandas as pd

import gymnasium as gym
from gymnasium import spaces


class TradingEnv(gym.Env):
    def __init__(self, ticker: str, window_size=5):
        super().__init__()
        self._window_size = window_size
        
        # --- Load data
        self.df = pd.read_csv(f"{ticker}.csv", parse_dates=True, index_col="timestamp")
        self.prices = self.df["close"].values

        # --- Environment state
        self._row_index = window_size
        self.position = 0  # 0 = flat, 1 = long
        self.entry_price = None

        # --- Observation & action spaces
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(window_size,),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(2)  # 0 = Hold, 1 = Buy

        # self.render_mode = 
        self.window = None
        self.clock = None
    
    def _get_observation(self):
        window = self.prices[self._row_index - self._window_size : self._row_index]
        # return np.array(window, dtype=np.float32)
        return window
    
    def reset(self, seed=None):
        self._row_index = self._window_size
        self.position = 0
        self.entry_price = None
        return self._get_observation(), {}

    def step(self, action):
        done = False
        reward = 0.0

        current_price = self.prices[self._row_index]

        # --- Action logic
        if action == 1 and self.position == 0:
            self.position = 1
            self.entry_price = current_price
        elif action == 0 and self.position == 1:
            reward = current_price - self.entry_price
            self.position = 0
            self.entry_price = None

        # --- Advance time
        self._row_index += 1
        if self._row_index >= len(self.prices):
            done = True

        obs = self._get_observation()
        return obs, reward, done, False, {}

    def render(self):
        print(f"t={self._row_index}, pos={self.position}, price={self.prices[self._row_index-1]:.2f}")
