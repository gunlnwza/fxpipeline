from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .base import Strategy

if TYPE_CHECKING:
    from ..backtest import Account, TimeHorizonDataFrame


class RandomAction(Strategy):
    def act(self, account: Account, data: TimeHorizonDataFrame):
        point = data.current_point()
        if not account.order:
            if np.random.random() < 0.5:
                account.buy(point)  # clearly need a np.array wrapper that expose current price, maybe a tiny pd.DataFrame design?
        else:
            if np.random.random() < 0.1:
                account.close(point)
