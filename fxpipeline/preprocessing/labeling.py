import numpy as np
import pandas as pd

from .pips import pip_diff
from .utils import smooth_boolean_series


def should_enter(pips: np.ndarray, sell: bool = False,
                 required_reward_to_risk: float = 2.0,
                 required_win: float = 200.0) -> bool:
    """Look at 'pips' shape and judge if it's a good trade."""
    if pips[0] != 0:
        raise ValueError("First value of 'pips' must be 0")

    if sell:
        pips *= -1

    max_win = max(pips)
    if max_win < required_win:
        return False
    max_win_index = np.where(pips == max_win)[0][0]

    pips_before_win = pips[:max_win_index]
    min_loss = min(pips_before_win) if len(pips_before_win) > 0 else 0

    reward_to_risk = float(max_win / abs(min_loss)) if min_loss < 0 else float("inf")
    return reward_to_risk >= required_reward_to_risk


# TODO[test]: this feels so experimental, make it tight
# IDEA: adjust pip dynamically on historical price, maybe by using zigzag indicator
def label_entry_signal(df: pd.DataFrame, pip: float = 0.0001, col: str = "close", **kwargs):
    """Label price df with smoothed should_enter column"""
    df = df.copy()

    future_rows = kwargs.pop("future_rows", 20)
    future_pips = pip_diff(df[col], pip, future_rows)

    name = "should_sell" if kwargs.get("sell") else "should_buy"
    sig = (
        future_pips.apply(lambda row: should_enter(row, **kwargs), raw=True, axis=1)
        .rename(name)
    )
    sig.index = df.index[:len(sig)]
    sig = smooth_boolean_series(sig, window=5)

    df = df.join(sig, how="outer")
    return df
