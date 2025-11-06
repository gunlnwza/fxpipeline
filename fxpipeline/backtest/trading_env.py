from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np

from gymnasium import spaces
import gymnasium as gym

from .data import Data
from .render import PygameRenderer, TerminalRenderer

if TYPE_CHECKING:
    import pandas as pd


class TradingEnv(gym.Env):
    metadata = {
        'render.modes': ['terminal', 'human'],
        'render_fps': 5
    }

    def __init__(self, df: pd.DataFrame, obs_size: int = 10, render_mode: Optional[str] = None):
        self.action_space = self._build_action_space()
        self.observation_space = self._build_observation_space(df, obs_size)

        self.data = Data(df, obs_size)
        self.renderer = self._build_renderer(render_mode)

    def _build_action_space(self):
        return spaces.Discrete(3, start=-1)

    def _build_observation_space(self, df, obs_size):
        shape = (len(df.columns), obs_size)
        return spaces.Box(-np.inf, np.inf, shape, np.float32)

    def _build_renderer(self, render_mode):
        if render_mode == "human":
            return PygameRenderer()
        elif render_mode == "terminal":
            return TerminalRenderer()
        return None

    def _get_observation(self):
        return self.data.get_observation()

    def _get_info(self):
        return self.data.get_info()

    def _interpret_action(self, action) -> float:
        reward = 0

        order = self.data.order
        if action == 1:
            if order and order._type == "sell":
                reward += self.data.close_order()
            if not order:
                self.data.buy()
        elif action == 0:
            if order:
                reward += self.data.close_order()
        elif action == -1:
            if order and order._type == "buy":
                reward += self.data.close_order()
            if not order:
                self.data.sell()

        return reward

    def step(self, action):
        """Update environment with actions"""
        observation = self._get_observation()
        info = self._get_info()
        reward = self._interpret_action(action)
        terminated = self.data.terminated
        truncated = self.render() or self.data.truncated
        self.data.step()
        return observation, reward, terminated, truncated, info

    def reset(self):
        """Reset environment to initial state"""
        self.data.reset()
        return self._get_observation(), self._get_info()

    def render(self) -> bool:
        """Visualize environment, return True if truncated"""
        truncated = False
        if self.renderer:
            truncated = self.renderer.render(self.data)
        return truncated

    def close(self):
        """Close environment, free stuffs"""
        if self.renderer:
            self.renderer.close()
