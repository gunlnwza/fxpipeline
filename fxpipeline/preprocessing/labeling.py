import numpy as np
import pandas as pd

from .pips import pip_diff
from .utils import smooth_boolean_series


def should_enter(pips: np.ndarray, sell: bool = False,
                 required_reward_to_risk: float = 2.0,
                 required_win: float = 200.0) -> bool:
    """Look at `pips` shape and judge if it would be a good trade."""
    if pips[0] != 0:
        raise ValueError("First value of 'pips' must be 0")
    if np.isnan(pips[-1]):  # right of price, not enough data to judge
        return None

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


# IDEA: adjust `required_win` dynamically based on historical price
def label_entry_signal(price_df: pd.DataFrame, pip: float = 0.0001,
                       col: str = "close", **kwargs) -> pd.DataFrame:
    """
    Label `price_df` with signal by looking at `col`
    
    Supported kwargs:
    - future_rows: int
    - sell: bool
    - required_reward_to_risk: float
    - required_win: float
    - smooth: bool
    """
    df = price_df.copy()
    future_rows = kwargs.pop("future_rows", 20)
    smooth = kwargs.pop("smooth", False)
    name = "should_sell" if kwargs.get("sell") else "should_buy"

    future_pips = pip_diff(df[col], pip, future_rows)
    sig = (
        future_pips.apply(lambda row: should_enter(row, **kwargs), raw=True, axis=1)
        .rename(name)
    )
    if smooth:
        sig = smooth_boolean_series(sig, window=5)  # the method cause lag in labelings

    sig.index = df.index[:len(sig)]
    df = df.join(sig, how="outer")

    return df
