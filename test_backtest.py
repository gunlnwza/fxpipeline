import numpy as np
import pandas as pd

from fxpipeline.core import CurrencyPair, ForexPrices, Data
from fxpipeline.ingestion import load_forex_prices
from fxpipeline.backtest import Backtester, Strategy


if __name__ == "__main__":
    df = pd.DataFrame([
        [1.5, 1.9, 1.1, 1.7],
        [2.5, 2.9, 2.1, 2.7],
        [3.5, 3.9, 3.1, 3.7],
        [4.5, 4.9, 4.1, 4.7], 
        [5.5, 5.9, 5.1, 5.7],
        [6.5, 6.9, 6.1, 6.7],
        [7.5, 7.9, 7.1, 7.7],
        [8.5, 8.9, 8.1, 8.7],
        [9.5, 9.9, 9.1, 9.7],
        [10.5, 10.9, 10.1, 10.7]
    ])

    d = Data(ForexPrices(CurrencyPair("ABC", "DEF", pip=0.0001), "mock", df))
    st = Strategy()

    bt = Backtester(d, st)
    bt.run()
    print("[ Backtest Result ]")
    print("Pips:", bt.pips)
