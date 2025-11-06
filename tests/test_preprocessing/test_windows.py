from statistics import mean, pstdev

import pandas as pd
import pytest

from fxpipeline.preprocessing import get_windows, get_normalized_windows

series = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).rename("name")
short_series = pd.Series([0, 1, 2, 3, 4]).rename("short")

w = get_windows(series, 5, 1)
nw = get_normalized_windows(series, 5, 1)


# --- get_windows()

def test_get_windows_index():
    assert w.index.to_list() == [0, 1, 2, 3, 4]

def test_get_windows_columns():
    assert w.columns.to_list() == ["name-4", "name-3", "name-2", "name-1", "name-0", "name+1"]

def test_get_windows_values():    
    for i in range(5):
        assert w.iloc[i].to_list() == [i, i + 1, i + 2, i + 3, i + 4, i + 5]

def test_get_windows_too_short():
    with pytest.raises(ValueError):
        get_windows(short_series, 5, 1)


# --- get_normalized_windows()

def test_get_normalized_windows_index():
    assert nw.index.to_list() == [0, 1, 2, 3, 4]

def test_get_normalized_windows_columns():
    assert nw.columns.to_list() == ["z-4", "z-3", "z-2", "z-1", "z-0", "z+1", "mean", "std"]

def test_get_normalized_windows_values():
    for i in range(5):
        lst = [i, i + 1, i + 2, i + 3, i + 4, i + 5]
        lst = [(i - mean(lst)) / pstdev(lst) for i in lst] + [mean(lst), pstdev(lst)]
        assert nw.iloc[i].to_list() == pytest.approx(lst, abs=1e-6)

def test_get_normalized_windows_too_short():
    with pytest.raises(ValueError):
        get_normalized_windows(short_series, 5, 1)
