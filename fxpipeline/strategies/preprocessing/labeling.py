import numpy as np
import pandas as pd

from .pips import pip_diff


def should_enter(
    pips: np.ndarray, sell: bool = False, win_pips: int = 200, loss_pips: int = 200
) -> bool | None:
    """Look at `pips` shape and judge if it would be a good trade."""
    if pips[0] != 0:
        raise ValueError("First value of 'pips' must be 0")
    if np.isnan(pips[-1]):  # right of price, not enough data to judge
        return None

    if sell:
        pips = -pips

    max_win = max(pips)
    if max_win < win_pips:
        return False
    max_win_index = np.where(pips == max_win)[0][0]

    pips_before_win = pips[:max_win_index]
    if len(pips_before_win) > 0:
        min_loss = min(pips_before_win)
        if min_loss < -loss_pips:
            return False

    return True


# IDEA: adjust `required_win` dynamically based on historical price
def label_entry_signal(
    price_df: pd.DataFrame, pip: float = 0.0001, col: str = "close", **kwargs
) -> pd.DataFrame:
    """
    Label `price_df` with signal by looking at `col`

    Supported kwargs:
    - future_rows: int = 20
    - sell: bool = False
    - win_pips: int = 200
    - loss_pips: int = 200
    """
    df = price_df.copy()
    future_rows = kwargs.pop("future_rows", 20)
    name = "should_sell" if kwargs.get("sell") else "should_buy"

    if name in df.columns:
        df.drop(name, axis=1, inplace=True)

    future_pips = pip_diff(df[col], pip, future_rows)
    sig = []
    for i in range(len(future_pips)):
        sig.append(should_enter(future_pips.iloc[i].to_numpy(), **kwargs))
    sig = pd.Series(sig, dtype="bool", name=name)

    sig.index = df.index[: len(sig)]
    df = df.join(sig, how="outer")
    return df
