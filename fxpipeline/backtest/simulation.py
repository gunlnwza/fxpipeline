from __future__ import annotations

import numpy as np
from typing import TYPE_CHECKING

from .account import Account
from .price import PricePoint

if TYPE_CHECKING:
    from ..strategy import Strategy


class Simulation:
    def __init__(self, data: np.array, strategy: Strategy, account: Account):
        self.data = data  # TODO: make data good, support index and time
        self.strategy = strategy
        self.account = account

        self.summary = None

    def run(self):
        for i in range(1, len(self.data)):
            point = PricePoint(i, self.data[i])
            if self.account.equity(point) <= 0:
                break
            self.strategy.act(self.account, point)

        if self.account.order:
            self.account.close(point)

        self.summary = {"account": self.account.stats.to_dict()} 
