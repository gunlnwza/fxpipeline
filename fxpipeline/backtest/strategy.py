from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..backtest import Account, TimeHorizonDataFrame


class Strategy(ABC):
    @abstractmethod
    def act(self, account: Account, data: TimeHorizonDataFrame):  # TODO[architecure]: make act() signature good
        pass


class RandomAction(Strategy):
    def act(self, account: Account, data: TimeHorizonDataFrame):
        point = data.current_point()
        if not account.order:
            if np.random.random() < 0.05:
                account.buy(point)  # clearly need a np.array wrapper that expose current price, maybe a tiny pd.DataFrame design?
        else:
            if np.random.random() < 0.05:
                account.close(point)
