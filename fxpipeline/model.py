import os

import pandas as pd
import numpy as np

import joblib
from sklearn.ensemble import RandomForestRegressor


class Model:
    def __init__(self):
        self._filename = "baseline.joblib"
        if os.path.exists(self._filename):
            self._model = joblib.load(self._filename)
            self._trained = True
        else:
            self._model = RandomForestRegressor(random_state=42)
            self._trained = False

    def fit(self, X_train, y_train):
        assert self._trained == False
        self._model.fit(X_train, y_train)
        self._trained = True
        joblib.dump(self._model, self._filename)

    def predict(self, X):
        y_pred = self._model.predict(X)
        return y_pred


def preprocess(closes: pd.DataFrame, n=100):
    """
    take in df with 'close', make rows of z's, mean, std
    """
    close_names = [f"close-{i}" for i in range(n)]

    prices = closes.copy()
    for i in range(n):
        prices[f"close-{i}"] = prices['close'].shift(i)
    prices["close+1"] = prices['close'].shift(-1)

    prices["mean"] = prices[close_names].mean(axis=1)
    prices["std"] = prices[close_names].std(axis=1)
    for i in range(n):
        prices[f"z-{i}"] = (prices[f"close-{i}"] - prices["mean"]) / prices["std"]
    prices[f"z+1"] = (prices[f"close+1"] - prices["mean"]) / prices["std"]

    prices.dropna(inplace=True)

    return prices


def evaluate_performance(y_test, y_pred):
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


if __name__ == "__main__":
    from sklearn.model_selection import TimeSeriesSplit

    from utils import Stopwatch

    df = pd.read_csv("data/.alpha_vantage_cache/USDJPY.csv")  # TODO[Loading]: loading is too low level, I want it polished and posh

    n = 100
    prices = preprocess(df[["close"]], n)
    z_names = [f"z-{i}" for i in range(n)]
    X = np.array(prices[z_names + ["mean", "std"]])
    y = np.array(prices["z+1"])

    sw = Stopwatch()
    model = Model()
    tscv = TimeSeriesSplit(2)
    for train_index, test_index in tscv.split(X):
        sw.start()
        
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        print(f"Train: [{train_index[0]}, {train_index[-1]}] | Test: [{test_index[0]}, {test_index[-1]}]")
        print()

        if not model._trained:
            print("Training on train portion...")
            model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print("Evaluating on test portion...")
        evaluate_performance(y_test, y_pred)

        sw.stop()
        print()
        print(f"Time elapse: {sw.time:.3f}s")
        print("-" * 80)
