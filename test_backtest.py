from dotenv import load_dotenv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

from fxpipeline.core import Data, ForexPrices, CurrencyPair
from fxpipeline.ingestion import load_forex_prices
from fxpipeline.backtest import Backtester, Strategy
from fxpipeline.utils import Stopwatch

import random


if __name__ == "__main__":
    load_dotenv()

    # df = pd.DataFrame([
    #     [1.5, 1.9, 1.1, 1.7, 0],
    #     [2.5, 2.9, 2.1, 2.7, 0],
    #     [3.5, 3.9, 3.1, 3.7, 0],
    #     [4.5, 4.9, 4.1, 4.7, 0],
    #     [5.5, 5.9, 5.1, 5.7, 0],
    #     [6.5, 6.9, 6.1, 6.7, 0],
    #     [7.5, 7.9, 7.1, 7.7, 0],
    #     [8.5, 8.9, 8.1, 8.7, 0],
    #     [9.5, 9.9, 9.1, 9.7, 0],
    #     [10.5, 10.9, 10.1, 10.7, 0]
    # ])

    # n = 5000
    # rng = np.random.default_rng(42)

    # closes = 100 + rng.normal(0, 0.01, n).cumsum()

    # opens = np.empty(n)
    # opens[0] = closes[0]
    # opens[1:] = closes[:-1] + rng.normal(0, 0.005, n - 1)

    # body_high = np.maximum(opens, closes)
    # body_low  = np.minimum(opens, closes)

    # wick_up = rng.exponential(0.004, n)
    # wick_dn = rng.exponential(0.004, n)

    # highs = body_high + wick_up
    # lows  = body_low - wick_dn

    # df = pd.DataFrame({
    #     "Open": opens,
    #     "High": highs,
    #     "Low": lows,
    #     "Close": closes,
    #     "Volume": 0
    # }, index=pd.date_range(start='2000-01-01', periods=n, freq='D'))

    # mpf.plot(df, 
    #     type='candle', 
    #     ylabel='Price ($)', 
    #     style='yahoo',
    #     volume=True
    # )

    # prices = ForexPrices(CurrencyPair("ABC", "DEF", 0.0001), "mock", df)
    prices = load_forex_prices("GBPUSD", source="alpha_vantage")

    data = Data(prices)
    strategy = Strategy()
    bt = Backtester(data, strategy)

    sw = Stopwatch()
    bt.run()

    print("Pips:", bt.pips)
    print("Time:", sw)
    print()

    plt.plot(bt._pips_list)
    plt.title("Buy if cur_close > prev_close, with 2:1 reward-to-risk")
    plt.axhline(0, ls="--", color="black")
    plt.show()
