import numpy as np

from fxpipeline.preprocessing.trades import should_enter

T = 1
N = 1000
deltatime = T / N
t = np.full(N, deltatime).cumsum()


def test_clear_win():
    diff = 1000 * t
    enter = should_enter(diff)
    assert enter is True


def test_clear_loss():
    diff = -1000 * t
    enter = should_enter(diff)
    assert enter is False


def test_draw():
    diff = 50 * np.sin(5 * 2*np.pi * t)
    enter = should_enter(diff)
    assert enter is False


def test_win_in_the_middle():
    diff = 1000 * (np.exp(-(4*(t - 0.5))**2) - np.exp(-4))
    enter = should_enter(diff)
    assert enter is True


def test_small_drawdown_before_win():
    diff = -10500 * t * (t - 0.3) * (t - 1)
    enter = should_enter(diff)
    assert enter is True


def test_large_drawdown_before_win():
    diff = -19000 * t * (t - 0.5) * (t - 1)
    enter = should_enter(diff)
    assert enter is False


def test_large_drawdown_no_win():
    diff = -11000 * t * (t - 0.7) * (t - 0.95)
    enter = should_enter(diff)
    assert enter is False
