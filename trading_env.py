import time

import pandas as pd
import numpy as np
import pygame as pg

from gymnasium import spaces
import gymnasium as gym

from fxpipeline.data import load_forex_price
from fxpipeline.utils import handle_sigint


class TradingEnv(gym.Env):
    def __init__(self, df: pd.DataFrame, obs_size=10, render_mode=None):
        self.spec = None
        self.metadata = None
        self.np_random = None

        # pygame
        self.render_mode = render_mode
        if render_mode == "human":
            pg.display.init()
            self.screen = pg.display.set_mode((500, 500))
            self.clock = pg.time.Clock()
            self.fps = 5

        # data
        self._df = df
        self._closes = df['close'].to_numpy()
        self._obs_size = obs_size

        # environment state
        self._i = obs_size

        # observation & action spaces
        self.action_space = spaces.Discrete(3, start=-1)  # -1 = sell, 0 = hold, 1 = buy
        self.observation_space = spaces.Box(-np.inf, np.inf, (1, obs_size), np.float32)

    def _get_obs(self):
        closes = self._closes[self._i - self._obs_size : self._i]
        closes = (closes - closes.mean()) / closes.std()
        return closes

    def step(self, action):
        """Update environment with actions"""
        obs = self._get_obs()

        cur_price = obs[-1]
        prev_price = obs[-2]

        # TODO: use Order's pnl logic
        pnl = 0
        if action == 1:
            pnl = cur_price - prev_price
        elif action == -1:
            pnl = -(cur_price - prev_price)
        reward = pnl

        info = {}
        done = self.render()
        if done:
            return obs, reward, done, False, info

        # advance time
        self._i += 1
        done = self._i >= len(self._closes)
        return obs, reward, done, False, info

    def reset(self, seed=None):
        """Reset environment to initial state"""
        self._i = self._obs_size
        return self._get_obs(), {}

    def render(self):
        """Visualize what the agent sees"""
        obs = self._get_obs()
        if self.render_mode == "terminal":
            print(f"i = {self._i}")
        elif self.render_mode == "human":
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                    self.close()
                    self.render_mode = None
                    return True

            w = self.screen.get_width()
            h = self.screen.get_height()

            def to_screen_x(x):
                return 10 + (w // (len(obs) + 1)) * x

            def to_screen_y(x):
                return h // 2 - x * h // 10

            self.screen.fill("black")
            for i in range(len(obs) - 1):
                start = (to_screen_x(i), to_screen_y(obs[i]))
                end = (to_screen_x(i + 1), to_screen_y(obs[i + 1]))
                pg.draw.line(self.screen, "white", start, end, 1)

            pg.display.flip()
            self.clock.tick(self.fps)

        return False

    def close(self):
        """Close environemnt, free stuffs"""
        if self.render_mode == "human":
            pg.quit()


class DummyModel:
    def __init__(self):
        pass

    def predict(self, obs):
        action = 0
        return action, {}


def main():
    handle_sigint()

    df = load_forex_price("EURUSD")
    env = TradingEnv(df, obs_size=50, render_mode="human")
    model = DummyModel()

    obs, _ = env.reset()
    while True:
        action, states = model.predict(obs)
        obs, reward, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            break

    env.close()


if __name__ == "__main__":
    main()
