import pandas as pd
import pytest

from fxpipeline.preprocessing import get_windows, get_standard_windows


# --- get_windows


def test_get_windows():
    series = pd.Series([0, 1, 2, 3, 4, 5]).rename("name")
    windows = get_windows(series, 3, 1)

    expected = pd.DataFrame(
        [
            [None, None, 0, 1],
            [None, 0, 1, 2],
            [0, 1, 2, 3],
            [1, 2, 3, 4],
            [2, 3, 4, 5],
            [3, 4, 5, None],
        ],
        columns=["name-2", "name-1", "name-0", "name+1"],
    )

    pd.testing.assert_frame_equal(windows, expected)


def test_get_windows_too_short():
    series = pd.Series([0, 1, 2]).rename("short")
    with pytest.raises(ValueError):
        get_windows(series, 3, 1)


# --- get_standard_windows


def test_get_standard_windows():
    series = pd.Series([0, 1, 4, 9, 16, 25]).rename("name")
    nw = get_standard_windows(series, 3, 1)

    expected = pd.DataFrame(
        [
            [None, None, None, None, 0, None],
            [None, -0.7071, 0.7071, 4.9497, 0.5, 0.7071],
            [-0.8006, -0.3203, 1.1209, 3.5228, 1.6667, 2.0817],
            [-0.9073, -0.165, 1.0722, 2.8043, 4.6667, 4.0415],
            [-0.9401, -0.1106, 1.0507, 2.5438, 9.6667, 6.0277],
            [-0.9558, -0.0831, 1.039, None, 16.6667, 8.0208],
        ],
        columns=["z_name-2", "z_name-1", "z_name-0", "z_name+1", "mean", "std"],
    )
    pd.testing.assert_frame_equal(nw, expected, atol=1e-4)
