from typing import TYPE_CHECKING

import pandas as pd
import numpy as np
import pygame as pg

from gymnasium import spaces
import gymnasium as gym

from ..data import load_forex_price
from ..utils import handle_sigint

if TYPE_CHECKING:
    import pandas as pd


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
            # self.fps = 20
            self.fps = 5

        # data
        self._df = df
        self._closes = df['close'].to_numpy()
        self._obs_size = obs_size

        self.order = 0
        self.open_point = None
        self.total_pips = 0

        self.hist = []

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
        prices = self._closes[self._i - self._obs_size : self._i]

        # TODO: use Order's pnl logic
        reward = 0
        if self.order == 1:
            if action == -1:
                reward = prices[-1] - self.open_point[1]
                self.order = -1
                self.open_point = (self._i, prices[-1])
            elif action == 0:
                reward = prices[-1] - self.open_point[1]
                self.order = 0
                self.open_point = (self._i, prices[-1])
        elif self.order == -1:
            if action == 1:
                reward = -(prices[-1] - self.open_point[1])
                self.order = 1
                self.open_point = (self._i, prices[-1])
            elif action == 0:
                reward = -(prices[-1] - self.open_point[1])
                self.order = 0
                self.open_point = (self._i, prices[-1])
        else:
            if action == 1:
                self.order = 1
                self.open_point = (self._i, prices[-1])
            elif action == -1:
                self.order = -1
                self.open_point = (self._i, prices[-1])
    
        self.total_pips += round(reward * 10000)
        self.hist.append(self.total_pips)

        obs = self._get_obs()
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
            print(f"i={self._i}, order={self.order}, pips={self.total_pips}")
        elif self.render_mode == "human":
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.close()
                    return True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        self.close()
                        return True
                    elif event.key == pg.K_a:
                        if self.fps - 4 > 0:
                            self.fps -= 4
                    elif event.key == pg.K_d:
                        if self.fps + 4 <= 20:
                            self.fps += 4

            w = self.screen.get_width()
            h = self.screen.get_height()

            def to_screen_x(index):
                return 10 + (w // (len(obs) + 1)) * index

            def to_screen_y(price):
                return h - ((price - min_price * 0.99) / (max_price * 1.01 - min_price * 0.99)) * h


            self.screen.fill("black")
            prices = self._closes[self._i - self._obs_size : self._i]
            max_price = max(prices)
            min_price = min(prices)
            for i in range(len(prices) - 1):
                start = (to_screen_x(i), to_screen_y(prices[i]))
                end = (to_screen_x(i + 1), to_screen_y(prices[i + 1]))
                pg.draw.line(self.screen, "white", start, end, 1)

            if self.order != 0:
                start = (0, to_screen_y(self.open_point[1]))
                end = (w, to_screen_y(self.open_point[1]))
                color = "green" if self.order == 1 else "red"
                pg.draw.line(self.screen, color, start, end)

            pg.display.flip()
            self.clock.tick(self.fps)

        return False

    def close(self):
        """Close environemnt, free stuffs"""
        if self.render_mode == "human":
            pg.quit()
            self.render_mode = None


def main():
    from .model import Model
    import matplotlib.pyplot as plt

    handle_sigint()

    df = load_forex_price("EURUSD")
    env = TradingEnv(df, obs_size=50, render_mode="terminal")
    model = Model()

    obs, _ = env.reset()
    while True:
        obs = obs.reshape((1, -1))
        # print(obs)
        action, states = model.predict(obs)
        action = action[0]

        threshold = 0  # z-score
        if action > threshold:
            action = 1
        elif action < -threshold:
            action = -1
        else:
            action = 0

        obs, reward, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            break

    plt.axhline(0, color="black", lw=0.8)
    plt.plot(env.hist)
    plt.show()

    env.close()


if __name__ == "__main__":
    main()
