import numpy as np

from .base import Strategy


class RandomAction(Strategy):
    def act(self, account, point):
        if not account.order:
            if np.random.random() < 0.5:
                account.buy(point)  # clearly need a np.array wrapper that expose current price, maybe a tiny pd.DataFrame design?
        else:
            if np.random.random() < 0.1:
                account.close(point)
