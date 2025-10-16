from __future__ import annotations

from typing import TYPE_CHECKING

from .price import PricePoint, TimeHorizonDataFrame

if TYPE_CHECKING:
    import pandas as pd

    from .account import Account
    
    from ..strategy import Strategy


class Simulation:
    def __init__(self, data: pd.DataFrame, strategy: Strategy, account: Account):
        self.data = TimeHorizonDataFrame(data)  # TODO: maybe rename to SimulationData, wrapping TimeHorizonDataFrame
        self.strategy = strategy
        self.account = account

        self.summary = None

    def run(self):
        for _ in range(self.data.i, self.data.n):
            point = self.data.current_point()
            if self.account.equity(point) <= 0:
                break
            self.strategy.act(self.account, self.data)
            self.data.next()

        if self.account.order:
            self.account.close(point)

        self.summary = {"account": self.account.stats.to_dict()} 


if __name__ == "__main__":
    import numpy as np
    import pandas as pd
    # sim = Simulation()
    np.random.seed(42)
    n = 10
    df = TimeHorizonDataFrame(
        pd.DataFrame(np.full(n, 42) + np.random.normal(0.1, 1, n).cumsum())
    )
    df.next()
    for i in range(3):
        print(f"i = {i}")
        print(df.tail(), df.tail().loc[i])
        print()
        df.next()
