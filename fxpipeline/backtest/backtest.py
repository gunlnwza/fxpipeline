import numpy as np
import pandas as pd

from .strategy import Strategy
from ..core import Data


class Backtester:
    """
    ### Constraints
    - Show only latest 100 bars.
    - Only one trade at a time.
    """
    def __init__(self, data: Data, strategy: Strategy):
        self.data = data
        self.strategy = strategy

        self.bars = 5

    def run(self):
        i = 0
        ohlc_arr = np.zeros((self.bars, 4))

        for timestamp, row in self.data.price.df.iterrows():
            ohlc_arr[i] = row            


if __name__ == "__main__":
    data = Data(pd.DataFrame([
        [1, 1, 1, 1],
        [2, 2, 2, 2],
        [3, 3, 3, 3],
        [4, 4, 4, 4], 
        [5, 5, 5, 5],
        [6, 6, 6, 6],
        [7, 7, 7, 7],
        [8, 8, 8, 8],
        [9, 9, 9, 9],
        [10, 10, 10, 10]
    ]))
    print(data)
    strategy = Strategy()

    bt = Backtester(data, strategy)
    bt.run()
