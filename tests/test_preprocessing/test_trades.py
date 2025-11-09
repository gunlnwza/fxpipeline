import numpy as np
import pytest

from fxpipeline.preprocessing.trades import should_enter


def _make_lines(points: list[tuple[int, int]], n_points: int | None = None) -> np.ndarray:
    xs, ys = zip(*points)
    if n_points is None:
        n_points = int(xs[-1]) + 1
    x_full = np.linspace(xs[0], xs[-1], n_points)
    y_full = np.interp(x_full, xs, ys)
    return y_full


def test_not_start_at_zero():
    pips = _make_lines([(0, 1000), (100, 0)])
    with pytest.raises(ValueError):
        should_enter(pips)

    pips = _make_lines([(0, -1000), (100, 0)])
    with pytest.raises(ValueError):
        should_enter(pips)


def test_big_win():
    pips = _make_lines([(0, 0), (90, 1000), (100, 0)])
    assert should_enter(pips) is True


def test_big_loss():
    pips = _make_lines([(0, 0), (90, -1000), (100, 0)])
    assert should_enter(pips) is False


def test_middle_big_win():
    pips = _make_lines([(0, 0), (50, 1000), (100, 0)])
    assert should_enter(pips) is True


def test_middle_big_loss():
    pips = _make_lines([(0, 0), (50, -1000), (100, 0)])
    assert should_enter(pips) is False


def test_two_big_wins():
    pips = _make_lines([(0, 0), (25, 1000), (50, 0), (75, 1000), (100, 0)])
    assert should_enter(pips) is True


def test_two_big_losses():
    pips = _make_lines([(0, 0), (25, -1000), (50, 0), (75, -1000), (100, 0)])
    assert should_enter(pips) is False


def test_draw():
    pips = _make_lines([(0, 0), (10, 50), (20, -50), (30, 50), (40, -50),
                        (50, 50), (60, -50), (70, 50), (80, -50), (90, 50), (100, 0)])
    assert should_enter(pips) is False


def test_small_drawdown_big_win():
    pips = _make_lines([(0, 0), (20, -200), (80, 800), (100, 0)])
    assert should_enter(pips) is True


def test_small_drawdown_small_win():
    pips = _make_lines([(0, 0), (20, -200), (80, 200), (100, 0)])
    assert should_enter(pips) is False


def test_big_drawdown_big_win():
    pips = _make_lines([(0, 0), (20, -800), (80, 800), (100, 0)])
    assert should_enter(pips) is False


def test_big_drawdown_small_win():
    pips = _make_lines([(0, 0), (20, -800), (80, 200), (100, 0)])
    assert should_enter(pips) is False


def test_win_plateau():
    pips = _make_lines([(0, 0), (80, 900), (90, 1000), (100, 0)])
    assert should_enter(pips) is True
