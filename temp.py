import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fxpipeline.ingestion import load_forex_prices
from fxpipeline.preprocessing import label_entry_signal, smooth_series


def plot_signal(ax, signal: pd.Series, color: str):
    from fxpipeline.preprocessing.smoothing import series_to_segments
    segments = series_to_segments(signal)
    for state, l, r in segments:
        if state:
            ax.axvspan(signal.index[l], signal.index[r], color=color, alpha=0.3)


def main():
    data = load_forex_prices("EURUSD", "alpha_vantage")
    prices = data[0].df
    df = prices

    w = 5

    df = label_entry_signal(df, **{"future_rows": 100, "required_win": 500, "required_reward_to_risk": 3})
    df["smooth_should_buy"] = smooth_series(df["should_buy"], min_width=w)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f"min_width = {w}")
    axes[0].plot(df["close"], color="black")
    axes[1].plot(df["close"], color="black")
    plot_signal(axes[0], df["should_buy"], "green")
    plot_signal(axes[1], df["smooth_should_buy"], "green")
    plt.show()


if __name__ == "__main__":
    main()
