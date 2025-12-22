import pandas as pd

from fxpipeline.preprocessing.pips import pip_diff


def test_pip_diff_increase_JPY():
    prices = pd.Series([1.00, 1.01, 1.03, 1.06, 1.10]).rename("close")
    pip = 0.01

    res = pip_diff(prices, pip, future_rows=3)
    expected = pd.DataFrame(
        [
            [0, 1, 3, 6],
            [0, 2, 5, 9],
            [0, 3, 7, None],
            [0, 4, None, None],
            [0, None, None, None],
        ],
        columns=["pips-0", "pips+1", "pips+2", "pips+3"],
    )
    pd.testing.assert_frame_equal(res, expected)


def test_pip_diff_decrease_JPY():
    prices = pd.Series([1.00, 0.99, 0.97, 0.94, 0.90]).rename("close")
    pip = 0.01

    res = pip_diff(prices, pip, future_rows=3)
    expected = pd.DataFrame(
        [
            [0, -1, -3, -6],
            [0, -2, -5, -9],
            [0, -3, -7, None],
            [0, -4, None, None],
            [0, None, None, None],
        ],
        columns=["pips-0", "pips+1", "pips+2", "pips+3"],
    )
    pd.testing.assert_frame_equal(res, expected)


def test_pip_diff_increase():
    prices = pd.Series([1.0000, 1.0001, 1.0003, 1.0006, 1.0010]).rename("close")
    pip = 0.0001

    res = pip_diff(prices, pip, future_rows=3)
    expected = pd.DataFrame(
        [
            [0, 1, 3, 6],
            [0, 2, 5, 9],
            [0, 3, 7, None],
            [0, 4, None, None],
            [0, None, None, None],
        ],
        columns=["pips-0", "pips+1", "pips+2", "pips+3"],
    )
    pd.testing.assert_frame_equal(res, expected)
