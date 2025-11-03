import os

import pandas as pd
import numpy as np

import joblib
from sklearn.ensemble import RandomForestRegressor

from ..data import load_forex_price


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
        print(f"Save model to '{self._filename}'")

    def predict(self, X):
        y_pred = self._model.predict(X)
        return y_pred


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

    # NOTE: What if we predict Low and High, and let the model do the buy-low-sell-high strategy?
    # Would need two timeframes, big and small
    # - predict bounds on big timeframe
    # - then execute trades with precision in small timeframe
    # Actually, this match how retail traders trade, they look at H1, or H4, then go in with M15.
    # Some people use H4 and go in H1, or use D1, go in H1.

    df = load_forex_price("EURUSD")
    n = 100
    prices = preprocess(df["close"], n)
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
            print()

        y_pred = model.predict(X_test)
        print("Evaluating on test portion...")
        evaluate_performance(y_test, y_pred)
        print()

        sw.stop()
        print(f"Time elapse: {sw.time:.3f}s")
        print("-" * 80)
