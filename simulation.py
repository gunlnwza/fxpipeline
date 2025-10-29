import pprint

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fxpipeline.strategy import RandomAction
from fxpipeline.backtest import Account, Simulation


def plot_base():
    plt.title("Backtest Result")
    plt.xlabel("Index")
    plt.ylabel("Price")

def plot_price(arr):
    plt.plot(arr)

def plot_order(orders: list):
    for order in orders:
        plt.plot(order[:2], order[-2:], color="green", lw=2, ls="--", ms=5, marker="o",)


if __name__ == "__main__":
    # np.random.seed(42)

    n = 1000
    drift = 1
    vol = 0.8

    # Random walk drift (looks like sideway forex price)
    # arr = np.full(n, 42) + np.random.normal(drift, vol, n).cumsum()
    
    # GBM (looks just like actual forex price)
    T = 1
    time_step = T / n
    dt = np.full(n, time_step).cumsum()
    dW_t = np.random.normal(0, np.sqrt(time_step), n).cumsum()
    arr = 42 * np.exp((drift - vol**2 / 2) * dt + vol * dW_t)

    df = pd.DataFrame(arr)
    strategy = RandomAction()
    account = Account(100)

    simulation = Simulation(df, strategy, account)
    simulation.run()
    pprint.pprint(simulation.summary)

    plot_base()
    plot_price(arr)
    plot_order(simulation.summary["account"]["orders"])
    plt.show()
