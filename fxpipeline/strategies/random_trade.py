import random
from .base import Strategy

class RandomTradeStrategy(Strategy):
    name = "random_trade"

    def act(self, sim):
        if random.random() < 0.2:
            row = sim.current_ohlcv
            o = row["open"]
            h = row["high"]
            l = row["low"]
            c = row["close"]
            body = c - o
            height = h - l

            if body > 0:
                sim.open_buy(c + height, c - height, c + 3*height)
            else:
                sim.open_sell(c - height, c + height, c - 3*height)
