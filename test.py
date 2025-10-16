import pprint
import numpy as np
import matplotlib.pyplot as plt

from fxpipeline.strategy import RandomAction
from fxpipeline.backtest import Account, Simulation


def plot_result(summary: dict):
    orders = summary["account"]["orders"]

    plt.title("Backtest Result")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.plot(data)
    for o in orders:
        xs = [o.open_point.index, o.close_point.index]
        ys = [o.open_point.price, o.close_point.price]
        plt.plot(xs, ys, color="green", lw=2, ls="--", ms=5, marker="o",)
    plt.show()


if __name__ == "__main__":
    import pandas as pd

    np.random.seed(42)
    n = 10
    data = pd.DataFrame(
        np.full(n, 42) + np.random.normal(0.1, 1, n).cumsum()
    )
    strategy = RandomAction()
    account = Account(100)

    simulation = Simulation(data, strategy, account)
    simulation.run()
    pprint.pprint(simulation.summary)
    plot_result(simulation.summary)
