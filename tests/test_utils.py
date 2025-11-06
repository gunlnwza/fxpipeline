import time
import signal

import pytest

from fxpipeline.utils.signal_utils import _sigint_handler
from fxpipeline.utils import Stopwatch


def test_sigint_handler_exits():
    with pytest.raises(SystemExit):
        _sigint_handler(signal.SIGINT, None)


def test_stopwatch():
    tol = 0.01

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
