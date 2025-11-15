import pandas as pd

from fxpipeline.preprocessing.utils import smooth_boolean_series


def test_smooth_boolean_series():
    s = [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0]
    s = pd.Series(s).astype(bool)
    res = smooth_boolean_series(s, window=5)
    expected = pd.Series([False] * 7 + [None] * 4)
    assert res == expected

    s = [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1]
    s = pd.Series(s).astype(bool)
    res = smooth_boolean_series(s, window=5)
    expected = pd.Series([True] * 7 + [None] * 4)
    assert res == expected
