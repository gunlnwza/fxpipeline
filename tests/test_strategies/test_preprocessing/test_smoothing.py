import pandas as pd

from fxpipeline.strategies.preprocessing.smoothing import (
    series_to_segments,
    smooth_segments,
    segments_to_series,
)


def test_series_to_segments():
    series = pd.Series([True] * 5 + [False] * 5)

    res = series_to_segments(series)
    expected = [(True, 0, 5), (False, 5, 10)]
    assert res == expected


def test_smooth_segments():
    segments = [
        (True, 0, 44),
        (False, 44, 46),
        (True, 46, 47),
        (False, 47, 57),
        (True, 57, 61),
        (False, 61, 62),
        (True, 62, 75),
        (False, 75, 76),
        (True, 76, 78),
        (False, 78, 79),
        (True, 79, 80),
        (False, 80, 201),
    ]

    res = smooth_segments(segments)
    expected = [(True, 0, 44), (False, 44, 57), (True, 57, 75), (False, 75, 201)]
    assert res == expected


def test_segments_to_series():
    segments = [(True, 0, 5), (False, 5, 10)]

    res = segments_to_series(segments)
    expected = pd.Series([True] * 5 + [False] * 5)
    pd.testing.assert_series_equal(res, expected)
