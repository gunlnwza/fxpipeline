from dotenv import load_dotenv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fxpipeline.core import CurrencyPair, ForexPrices, Data
from fxpipeline.ingestion import load_forex_prices
from fxpipeline.backtest import Backtester, Strategy


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
    # prices = ForexPrices(CurrencyPair("ABC", "DEF", 0.0001), "mock", df)

    prices = load_forex_prices("USDJPY", source="alpha_vantage")

    data = Data(prices)
    st = Strategy()
    bt = Backtester(data, st)

    bt.run()
    plt.plot(bt._pips_list)
    plt.title("Buy if cur_close > prev_close, with 2:1 reward-to-risk")
    plt.axhline(0, ls="--", color="black")
    plt.show()
