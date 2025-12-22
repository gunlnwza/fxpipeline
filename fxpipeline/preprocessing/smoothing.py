import pandas as pd
import numpy as np


def series_to_segments(entry_signal: pd.Series) -> list[tuple[bool | int | int]]:
    s = entry_signal.to_numpy()
    last = -1
    segments = []
    for i in range(len(s) - 1):
        if s[i] != s[i + 1]:
            segments.append((bool(s[i]), last + 1, i + 1))
            last = i
    segments.append((bool(s[last + 1]), last + 1, len(s)))
    return segments


def smooth_segments(
    segments: list[tuple[bool | int | int]], min_width=3
) -> list[tuple[bool | int | int]]:
    """min_width=1 means no change"""

    # Filter out too short segments
    segments = [s for s in segments if s[2] - s[1] >= min_width]

    # Merge same segments
    i = 0
    new = []
    while i < len(segments):
        val, left, right = segments[i]
        while i < len(segments) - 1 and segments[i][0] == segments[i + 1][0]:
            right = segments[i + 1][2]
            i += 1
        new.append((val, left, right))
        i += 1
    segments = new

    # Extend bounds (from False segments)
    new = []
    for i in range(len(segments)):
        if segments[i][0] is False:
            left = segments[i - 1][2] if i - 1 >= 0 else 0
            right = segments[i + 1][1] if i + 1 < len(segments) else segments[i][2]
            new.append((False, left, right))
        else:
            new.append(segments[i])
    segments = new

    return segments


def segments_to_series(
    segments: list[tuple[bool | int | int]], length=None
) -> pd.Series:
    if length is None:
        length = max(r for _, _, r in segments)

    arr = np.empty(length, dtype=bool)
    for val, start, end in segments:
        arr[start:end] = val

    return pd.Series(arr)


def smooth_series(series: pd.Series, min_width=3) -> pd.Series:
    """Remove the little noisy segments"""
    segments = series_to_segments(series)
    segments = smooth_segments(segments, min_width)
    res = segments_to_series(segments)
    res.index = series.index
    return res
