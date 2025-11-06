from typing import TYPE_CHECKING, Optional

import pandas as pd
import numpy as np
import pygame as pg

from gymnasium import spaces
import gymnasium as gym

from ..data import load_forex_price
from ..utils import handle_sigint

if TYPE_CHECKING:
    import pandas as pd


class Order:
    def __init__(self, type: str, i: int, price: float):
        self._type = type.lower()
        assert self._type in ("buy", "sell")

        self._open_i = i
        self._open_price = price

        self._close_i = None
        self._close_price = None

    def get_info(self) -> dict:
        return {
            "type": self._type,
            "open_i": self._open_i, "open_price": self._open_price,
            "close_i": self._close_i, "close_price": self._close_price
        }

    def close(self, i, price):
        self._close_i = i
        self._close_price = price
    
    @property
    def profit(self):
        return self.current_profit(self._close_price)
    
    def current_profit(self, price):
        price_diff = price - self._open_price
        if self._type == "sell":
            price_diff *= -1
        return price_diff


class Data:
    def __init__(self, df, obs_size):
        # training/testing data
        self._df = df
        self._closes = df['close'].to_numpy()
        self._obs_size = obs_size

        # states
        self._i: int = self._obs_size  # window is [i - obs_size, i)
        self.order: Optional[Order] = None

        # info + log
        self.total_profit = 0

    def get_observation(self):
        closes = self._closes[self._i - self._obs_size : self._i]
        closes = (closes - closes.mean()) / closes.std()
        return closes

    def get_info(self):
        closes = self._closes[self._i - self._obs_size : self._i]

        info = {
            "i": self._i,
            "closes": closes,
            "total_profit": self.total_profit
        }
        if self.order:
            info["order"] = self.order.get_info()

        return info

    def step(self):
        if not self.is_truncated():
            self._i += 1

    def reset(self):
        self._i = self._obs_size
        self.order = None

    def is_terminated(self):
        return False

    def is_truncated(self):
        return self._i >= len(self._df)

    @property
    def current_price(self):
        return self._closes[self._i - 1]
    
    def buy(self):
        assert self.order is None
        self.order = Order("buy", self._i, self.current_price)

    def sell(self):
        assert self.order is None
        self.order = Order("sell", self._i, self.current_price)

    def close_order(self):
        assert self.order

        self.order.close(self._i, self.current_price)
        profit = self.order.profit
        self.order = None
        
        self.total_profit += profit
        
        return profit
    
    def current_profit(self):
        assert self.order
        return self.order.current_profit(self.current_price)


class Renderer:
    def __init__(self):
        pass

    def render(self, data: Data):
        truncated = False
        return truncated

    def close(self):
        pass

class PygameRenderer(Renderer):
    def __init__(self):
        pg.display.init()
        self.screen = pg.display.set_mode((500, 500))
        self.clock = pg.time.Clock()
        self.fps = 5

    def handle_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.close()
                return True
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_q:
                    self.close()
                    return True
                elif e.key == pg.K_a:
                    if self.fps - 4 > 0:
                        self.fps -= 4
                elif e.key == pg.K_d:
                    if self.fps + 4 <= 20:
                        self.fps += 4
        return False

    def render(self, data):
        truncated = self.handle_events()
        if truncated:
            return truncated

        info = data.get_info()
        closes = info["closes"]
        order = info.get("order")

        w = self.screen.get_width()
        h = self.screen.get_height()

        def to_screen_x(index):
            return 10 + (w // (len(closes) + 1)) * index

        def to_screen_y(price):
            return h - ((price - min_price * 0.99) / (max_price * 1.01 - min_price * 0.99)) * h

        self.screen.fill("black")
        max_price = max(closes)
        min_price = min(closes)
        for i in range(len(closes) - 1):
            start = (to_screen_x(i), to_screen_y(closes[i]))
            end = (to_screen_x(i + 1), to_screen_y(closes[i + 1]))
            pg.draw.line(self.screen, "white", start, end, 1)

        if order:
            start = (0, to_screen_y(order["open_price"]))
            end = (w, to_screen_y(order["open_price"]))
            color = "green" if order["type"] == "buy" else "red"
            pg.draw.line(self.screen, color, start, end)

        pg.display.flip()
        self.clock.tick(self.fps)

    def close(self):
        pg.quit()

class TerminalRenderer(Renderer):
    def __init__(self):
        pass

    def render(self, data):
        info = data.get_info()
        # order = info.get("order")
        print(f"i={info['i']}, total_profit={info['total_profit']:.4f}")


class TradingEnv(gym.Env):
    metadata = {
        'render.modes': ['terminal', 'human'],
        'render_fps': 5
    }

    def __init__(self, df: pd.DataFrame, obs_size=10, render_mode=None):
        self.action_space = self._build_action_space()
        self.observation_space = self._build_observation_space((1, obs_size))

        self.data = Data(df, obs_size)
        self.renderer = self._build_renderer(render_mode)

    def _build_action_space(self):
        return spaces.Discrete(3, start=-1)

    def _build_observation_space(self, shape):
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

        # if self.data.order and self.data.current_profit() < -0.0100:
        #     reward += self.data.close_order()

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
        reward = self._interpret_action(action)
        terminated = self.data.is_terminated()
        truncated = self.render() or self.data.is_truncated()
        info = self._get_info()
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


# TODO: This has to go, make wrappers instead
def get_action(model, obs):
    obs = obs.reshape((1, -1))
    action, states = model.predict(obs)
    action = action[0]

    threshold = 1  # z-score
    if action > threshold:
        action = 1
    elif action < -threshold:
        action = -1
    else:
        action = 0
    return action

def main():
    from .model import Model

    handle_sigint()

    df = load_forex_price("EURUSD")
    env = TradingEnv(df, obs_size=50, render_mode="human")
    model = Model()

    obs, info = env.reset()
    while True:
        action = get_action(model, obs)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    env.close()


if __name__ == "__main__":
    main()
