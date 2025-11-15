# import json

import pandas as pd


# maybe wrap pandas-ta instead?


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
