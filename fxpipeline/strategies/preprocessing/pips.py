import pandas as pd

from .windows import get_windows


def pip_diff(prices: pd.Series, pip: float, future_rows=20) -> pd.DataFrame:
    """Get window of future returns in pips"""
    future_price = get_windows(prices, 1, future_rows)
    name = prices.name

    future_pips = (
        future_price.filter(like=f"{name}+").subtract(future_price[f"{name}-0"], axis=0)
        / pip
    ).round()
    future_pips.columns = [col.replace(name, "pips") for col in future_pips.columns]
    future_pips.insert(0, "pips-0", 0)

    return future_pips
