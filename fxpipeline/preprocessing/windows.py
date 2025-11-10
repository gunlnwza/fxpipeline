import pandas as pd


def _get_name(prefix: str, i: int) -> str:
    """+ if future, - if already seen;"""
    if i < 0:
        return f"{prefix}+{abs(i)}"
    else:
        return f"{prefix}-{i}"


def get_windows(series: pd.Series, seen_rows=10, next_rows=1):
    """Plop rolling window into rows"""
    if len(series) < seen_rows + next_rows:
        raise ValueError("Series is too short to create rows")

    series_arr = []
    for i in range(-next_rows, seen_rows):
        s = series.shift(i)
        s.rename(_get_name(s.name, i), inplace=True)
        series_arr.append(s)
    series_arr.reverse()

    df = pd.concat(series_arr, axis=1)
    return df


def get_normalized_windows(series: pd.Series, seen_rows=10, next_rows=1):
    """Take in series; make rows of z-scores, mean, and std"""
    windows = get_windows(series, seen_rows, next_rows)
    windows["mean"] = windows.mean(axis=1)
    windows["std"] = windows.std(axis=1)

    for i in range(-next_rows, seen_rows):
        name = _get_name(series.name, i)
        windows[name] = (windows[name] - windows["mean"]) / windows["std"]

    windows.rename(columns={
        _get_name(series.name, i): _get_name("z", i) for i in range(-next_rows, seen_rows)
    }, inplace=True)

    return windows
