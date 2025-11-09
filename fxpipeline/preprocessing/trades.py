import numpy as np


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
