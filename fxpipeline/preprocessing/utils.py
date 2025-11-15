import pandas as pd
import numpy as np


def smooth_boolean_series(s: pd.Series, window: int = 5) -> pd.Series:
    rolling_mode = (
        s.rolling(window)
        .apply(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan, raw=False)
        .astype(bool)
    )
    return rolling_mode
