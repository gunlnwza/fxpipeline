import pandas as pd


def preprocess(closes: pd.Series, n=50):
    """
    Take in serie of 'closes' prices, make rows of z's, mean, std
    """
    def get_name(prefix: str, i: int) -> str:
        """
        + if future, - if already seen; Filtration, Yay!
        """
        if i < 0:
            return f"{prefix}+{abs(i)}"
        else:
            return f"{prefix}-{i}"

    close_series = []
    for i in range(-1, n):
        s = closes.shift(i)
        s = s.rename(get_name("close", i))
        close_series.append(s)
    close_df = pd.concat(close_series, axis=1)
    close_df.dropna(inplace=True)

    z_series = []
    mean = close_df.mean(axis=1).rename("mean")
    std = close_df.std(axis=1).rename("std")
    for i in range(-1, n):
        s = (close_df[get_name("close", i)] - mean) / std
        s = s.rename(get_name("z", i))
        z_series.append(s)

    res = pd.concat(z_series + [mean, std], axis=1)
    return res
