import numpy as np
import pandas as pd

from .windows import get_windows


def should_enter(pips: np.ndarray, *, sell: bool = False,
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


# TODO: pip_diffs() and smooth_boolean_series() are to be used with should_enter()
def pip_diffs(prices: pd.Series, pip: float, future_rows=20) -> pd.DataFrame:
    """Get window of future returns in pips"""
    future_price = get_windows(prices, 1, future_rows)
    name = prices.name

    future_pips = (
        future_price.filter(like=f"{name}+")
        .subtract(future_price[f"{name}-0"], axis=0)
        / pip
        ).round()
    future_pips.columns = [col.replace(name, "pips") for col in future_pips.columns]
    future_pips.insert(0, "pips-0", 0)

    return future_pips


# TODO[refactor]: Should move to preprocessing.utils instead.
def smooth_boolean_series(s: pd.Series, window: int = 5) -> pd.Series:
    rolling_mode = (
        s.rolling(window)
        .apply(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan, raw=False)
        .astype(bool)
    )
    return rolling_mode
