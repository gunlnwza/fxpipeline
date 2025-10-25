import json

import pandas as pd


def sma(df: pd.DataFrame, period=20, apply_on="close") -> pd.Series:
    s = df[apply_on].rolling(window=period, min_periods=period).mean()
    return s


def ema(df: pd.DataFrame, period=20, apply_on="close") -> pd.Series:
    s = df[apply_on].ewm(span=period, adjust=False).mean()
    return s


def rsi(df: pd.DataFrame, period=14, apply_on="close") -> pd.Series:
    delta = df[apply_on].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    s = 100 - (100 / (1 + rs))
    return s


def macd(df: pd.DataFrame, fast_period=12, slow_period=26,
         apply_on="close") -> pd.Series:
    s = ema(df, fast_period, apply_on) - ema(df, slow_period, apply_on)
    return s


INDICATORS = {
    "sma": sma,
    "ema": ema,
    "rsi": rsi,
    "macd": macd,
}


def load_indicator_configs(filename: str) -> list[dict]:
    with open(filename, "r") as infile:
        data = json.load(infile)
        return data


def apply_indicators(df: pd.DataFrame, configs: list[dict]) -> pd.DataFrame:
    """
    configs: list of dicts like
        {"name": "fast_ma", "type": "sma", "period": 20, "apply_on": "close"}
        {"name": "macd", "type": "macd", "fast_period": 12, "slow_period": 26}
    """
    for cfg in configs:
        name = cfg.pop("name")
        type_ = cfg.pop("type")  # e.g. "sma"
        func = INDICATORS.get(type_)
        if not func:
            raise ValueError(f"Unknown indicator '{type_}'")
        df[name] = func(df, **cfg)
    return df


def separate_timestamp(df: pd.DataFrame):
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day"] = df.index.day
    df = df.reset_index(drop=True)
    return df
