import pandas as pd

from fxpipeline.preprocessing.pips import pip_diff


def test_pip_diff_increase_JPY():
    prices = pd.Series([1.00, 1.01, 1.03, 1.06, 1.10]).rename("close")
    pip = 0.01

    res = pip_diff(prices, pip, future_rows=3)
    expected = pd.DataFrame({
        "pips-0": [0, 0, 0, 0, 0],
        "pips+1": [1, 2, 3, 4, None],
        "pips+2": [3, 5, 7, None, None],
        "pips+3": [6, 9, None, None, None],
    })
    assert res.equals(expected)


def test_pip_diff_decrease_JPY():
    prices = pd.Series([1.00, 0.99, 0.97, 0.94, 0.90]).rename("close")
    pip = 0.01

    res = pip_diff(prices, pip, future_rows=3)
    expected = pd.DataFrame({
        "pips-0": [0, 0, 0, 0, 0],
        "pips+1": [-1, -2, -3, -4, None],
        "pips+2": [-3, -5, -7, None, None],
        "pips+3": [-6, -9, None, None, None],
    })
    assert res.equals(expected)


def test_pip_diff_increase():
    prices = pd.Series([1.0000, 1.0001, 1.0003, 1.0006, 1.0010]).rename("close")
    pip = 0.0001

    res = pip_diff(prices, pip, future_rows=3)
    expected = pd.DataFrame({
        "pips-0": [0, 0, 0, 0, 0],
        "pips+1": [1, 2, 3, 4, None],
        "pips+2": [3, 5, 7, None, None],
        "pips+3": [6, 9, None, None, None],
    })
    assert res.equals(expected)
