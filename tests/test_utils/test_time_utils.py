import time

from fxpipeline.utils import Stopwatch


def test_stopwatch():
    tol = 0.010

    sw = Stopwatch()
    time.sleep(0.005)
    assert sw.time - 0.005 <= tol

    sw.start()
    time.sleep(0.050)
    assert sw.time - 0.050 <= tol

    sw.start()
    time.sleep(0.100)
    sw.stop()
    assert sw.time - 0.100 <= tol
