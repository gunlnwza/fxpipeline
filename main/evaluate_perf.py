import pandas as pd
import numpy as np

from sklearn.model_selection import TimeSeriesSplit

from fxpipeline.ingestion import load_forex_price
from fxpipeline.preprocessing import preprocess
from fxpipeline.strategy import Model
from fxpipeline.utils import Stopwatch


def evaluate_performance(y_test, y_pred):
    print(len(y_test), len(y_pred))
    df = pd.DataFrame({
        "y_test": y_test,
        "y_pred": y_pred
    })

    df["error"] = df['y_test'] - df['y_pred']
    df['price_diff'] = df['y_test'].diff().fillna(0)
    df["same_direction"] = df["y_test"] * df['y_pred'] > 0
    df['profit'] = abs(df['price_diff']) * (df["same_direction"] * 2 - 1)

    pnl = df['profit'].cumsum()
    pnl_cummax = pnl.cummax()
    drawdown = pnl_cummax - pnl

    win_rate = df["same_direction"].sum() / len(df)
    max_drawdown = max(drawdown)

    print(f"Win rate: {win_rate:.2f}")
    print(f"Pips gain: {pnl.iloc[-1] * 100:.0f}")
    print(f"Max drawdown in pips: {max_drawdown * 100:.0f}")


def main():
    # NOTE: What if we predict Low and High, and let the model do the buy-low-sell-high strategy?
    # Would need two timeframes, big and small
    # - predict bounds on big timeframe
    # - then execute trades with precision in small timeframe
    # Actually, this match how retail traders trade, they look at H1, or H4, then go in with M15.
    # Some people use H4 and go in H1, or use D1, go in H1.

    df = load_forex_price("EURUSD")
    n = 50
    prices = preprocess(df["close"], n)
    z_names = [f"z-{i}" for i in range(n)]
    X = np.array(prices[z_names])
    y = np.array(prices["z+1"])

    sw = Stopwatch()
    model = Model()
    tscv = TimeSeriesSplit(2)
    for train_index, test_index in tscv.split(X):
        sw.start()

        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        print(f"Train: [{train_index[0]}, {train_index[-1]}]"
              f"| Test: [{test_index[0]}, {test_index[-1]}]")
        print()

        if not model._trained:
            print("Training on train portion...")
            model.fit(X_train, y_train)
            print()

        y_pred = model.predict(X_test)
        print("Evaluating on test portion...")
        evaluate_performance(y_test, y_pred)
        print()

        sw.stop()
        print(f"Time elapse: {sw.time:.3f}s")
        print("-" * 80)


if __name__ == "__main__":
    main()
