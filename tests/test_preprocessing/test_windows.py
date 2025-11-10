from statistics import mean, pstdev

import pandas as pd
import pytest

from fxpipeline.preprocessing import get_windows, get_normalized_windows


def test_get_windows():
    series = pd.Series([0, 1, 2, 3, 4, 5]).rename("name")
    w = get_windows(series, seen_rows=3, future_rows=1)

    assert w.index.to_list() == [0, 1, 2, 3, 4, 5]
    assert w.columns.to_list() == ["name-2", "name-1", "name-0", "name+1"]

    expected = pd.DataFrame({
        "name-2": [None, None, 0, 1, 2, 3],
        "name-1": [None, 0, 1, 2, 3, 4],
        "name-0": [0, 1, 2, 3, 4, 5],
        "name+1": [1, 2, 3, 4, 5, None]
    })
    assert w.equals(expected)


def test_get_windows_too_short():
    with pytest.raises(ValueError):
        get_windows(pd.Series([0, 1, 2]).rename("short"), 3, 1)


def test_get_normalized_windows_index():
    series = pd.Series([0, 1, 2, 3, 4, 5]).rename("name")
    nw = get_normalized_windows(series, seen_rows=3, future_rows=1)

    assert nw.index.to_list() == [0, 1, 2, 3, 4, 5]
    assert nw.columns.to_list() == ["z-2", "z-1", "z-0", "z+1", "mean", "std"]

    expected = pd.DataFrame({
        "z-2": [None, None, -1.341641, -1.341641, -1.341641, -1.224745],
        "z-1": [None, -1.224745, -0.447214, -0.447214, -0.447214, 0],
        "z-0": [-1, 0, 0.447214, 0.447214, 0.447214, 1.224745],
        "z+1": [1, 1.224745, 1.341641, 1.341641, 1.341641, None],
        "mean": [0.5, 1, 1.5, 2.5, 3.5, 4],
        "std": [0.5, 0.816497, 1.118034, 1.118034, 1.118034, 0.816497]
    })
    pd.testing.assert_frame_equal(nw, expected, rtol=1e-6, atol=1e-6)
