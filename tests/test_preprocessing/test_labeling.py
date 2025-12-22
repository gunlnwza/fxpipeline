import pandas as pd
import numpy as np
import pytest

from fxpipeline.preprocessing.labeling import should_enter, label_entry_signal


def _make_lines(
    points: list[tuple[int, int]], n_points: int | None = None
) -> np.ndarray:
    xs, ys = zip(*points)
    if n_points is None:
        n_points = int(xs[-1]) + 1
    x_full = np.linspace(xs[0], xs[-1], n_points)
    y_full = np.interp(x_full, xs, ys)
    return y_full


# --- should_enter


def test_not_start_at_zero():
    pips = _make_lines([(0, 1000), (100, 0)])
    with pytest.raises(ValueError):
        should_enter(pips)

    pips = _make_lines([(0, -1000), (100, 0)])
    with pytest.raises(ValueError):
        should_enter(pips)


def test_big_up():
    pips = _make_lines([(0, 0), (90, 1000), (100, 0)])
    assert should_enter(pips) is True
    assert should_enter(pips, sell=True) is False


def test_big_down():
    pips = _make_lines([(0, 0), (90, -1000), (100, 0)])
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is True


def test_middle_big_up():
    pips = _make_lines([(0, 0), (50, 1000), (100, 0)])
    assert should_enter(pips) is True
    assert should_enter(pips, sell=True) is False


def test_middle_big_down():
    pips = _make_lines([(0, 0), (50, -1000), (100, 0)])
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is True


def test_draw():
    pips = _make_lines(
        [
            (0, 0),
            (10, 50),
            (20, -50),
            (30, 50),
            (40, -50),
            (50, 50),
            (60, -50),
            (70, 50),
            (80, -50),
            (90, 50),
            (100, 0),
        ]
    )
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is False


def test_two_big_ups():
    pips = _make_lines([(0, 0), (25, 1000), (50, 0), (75, 1000), (100, 0)])
    assert should_enter(pips) is True
    assert should_enter(pips, sell=True) is False


def test_two_big_downs():
    pips = _make_lines([(0, 0), (25, -1000), (50, 0), (75, -1000), (100, 0)])
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is True


def test_small_down_big_up():
    pips = _make_lines([(0, 0), (20, -200), (80, 800), (100, 0)])
    assert should_enter(pips) is True
    assert should_enter(pips, sell=True) is True


def test_small_down_small_up():
    pips = _make_lines([(0, 0), (20, -150), (80, 150), (100, 0)])
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is False


def test_big_down_big_up():
    pips = _make_lines([(0, 0), (20, -800), (80, 800), (100, 0)])
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is True


def test_big_down_small_up():
    pips = _make_lines([(0, 0), (20, -800), (80, 200), (100, 0)])
    assert should_enter(pips) is False
    assert should_enter(pips, sell=True) is True


def test_plateau_up():
    pips = _make_lines([(0, 0), (80, 900), (90, 1000), (100, 0)])
    assert should_enter(pips) is True
    assert should_enter(pips, sell=True) is False


# --- label_entry_signal


def test_label_entry_signal():
    price_df = pd.DataFrame({"close": [1, 2, 3, 4, 5, 10, 9, 8, 7, 6]})
    price_df = label_entry_signal(price_df, pip=0.0001, **{"future_rows": 1})

    expected = price_df.copy()
    expected["should_buy"] = pd.Series(  # last entry shall be False
        [True, True, True, True, True, False, False, False, False, False], dtype="bool"
    )
    pd.testing.assert_frame_equal(price_df, expected)
