import numpy as np

from ...backtest.base import Data


class RandomBuy(SignalGenerator):
    def __init__(self, buy_prob=0.5, random_state=None):
        self._rng = np.random.default_rng(random_state)
        self.buy_prob = buy_prob

    def generate_batch(self, data: Data):
        b = self.buy_prob
        return self._rng.choice([0, 1], len(data), p=[1 - b, b])


class BuyAndHold(SignalGenerator):
    def generate_batch(self, data: Data):
        arr = np.ones(len(data))
        return arr
