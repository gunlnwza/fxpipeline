import pandas as pd

from fxpipeline.preprocessing.trades import pip_diffs, smooth_boolean_series


def test_pip_diffs_increase_JPY():
    prices = pd.Series([1.00, 1.01, 1.03, 1.06, 1.10]).rename("close")
    pip = 0.01

    res = pip_diffs(prices, pip, future_rows=3)
    expected = pd.DataFrame({
        "pips-0": [0, 0, 0, 0, 0],
        "pips+1": [1, 2, 3, 4, None],
        "pips+2": [3, 5, 7, None, None],
        "pips+3": [6, 9, None, None, None],
    })
    assert res.equals(expected)

    
def test_pip_diffs_decrease_JPY():
    prices = pd.Series([1.00, 0.99, 0.97, 0.94, 0.90]).rename("close")
    pip = 0.01

    res = pip_diffs(prices, pip, future_rows=3)
    expected = pd.DataFrame({
        "pips-0": [0, 0, 0, 0, 0],
        "pips+1": [-1, -2, -3, -4, None],
        "pips+2": [-3, -5, -7, None, None],
        "pips+3": [-6, -9, None, None, None],
    })
    assert res.equals(expected)


def test_pip_diffs_increase():
    prices = pd.Series([1.0000, 1.0001, 1.0003, 1.0006, 1.0010]).rename("close")
    pip = 0.0001

    res = pip_diffs(prices, pip, future_rows=3)
    expected = pd.DataFrame({
        "pips-0": [0, 0, 0, 0, 0],
        "pips+1": [1, 2, 3, 4, None],
        "pips+2": [3, 5, 7, None, None],
        "pips+3": [6, 9, None, None, None],
    })
    assert res.equals(expected)


# def test_smooth_boolean_series():
#     s = [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0]
#     s = pd.Series(s).astype(bool)
#     res = smooth_boolean_series(s, window=5)
#     expected = pd.Series([False] * 7 + [None] * 4)
#     assert res == expected

#     s = [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1]
#     s = pd.Series(s).astype(bool)
#     res = smooth_boolean_series(s, window=5)
#     expected = pd.Series([True] * 7 + [None] * 4)
#     assert res == expected
