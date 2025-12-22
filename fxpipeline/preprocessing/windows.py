import pandas as pd


def _get_name(prefix: str, i: int) -> str:
    """+ if future, - if already seen;"""
    if i < 0:
        return f"{prefix}+{abs(i)}"
    else:
        return f"{prefix}-{i}"


def get_windows(series: pd.Series, seen_rows=20, future_rows=0):
    """Apply rolling windows to rows"""
    if len(series) < seen_rows + future_rows:
        raise ValueError("Series is too short to create rows")

    series_arr = []
    for i in range(-future_rows, seen_rows):
        s = series.shift(i)
        s.rename(_get_name(s.name, i), inplace=True)
        series_arr.append(s)
    series_arr.reverse()

    df = pd.concat(series_arr, axis=1)
    return df


def get_standard_windows(
    series: pd.Series, seen_rows=20, future_rows=0, mean=None, std=None
):
    """Apply rolling windows to rows, then apply standardization on *only* seen rows"""
    windows = get_windows(series, seen_rows, future_rows)
    s_name = series.name
    cols = [_get_name(s_name, i) for i in range(0, seen_rows)]

    if mean is None:
        mean = windows[cols].mean(axis=1)
    if std is None:
        std = windows[cols].std(axis=1)
    windows["mean"] = mean
    windows["std"] = std

    for i in range(-future_rows, seen_rows):
        name = _get_name(s_name, i)
        windows[name] = (windows[name] - mean) / std

    windows.rename(
        columns={
            _get_name(s_name, i): _get_name(f"z_{s_name}", i)
            for i in range(-future_rows, seen_rows)
        },
        inplace=True,
    )

    return windows
