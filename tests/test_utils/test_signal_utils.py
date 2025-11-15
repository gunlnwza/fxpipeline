import signal

import pytest

from fxpipeline.utils.signal_utils import _sigint_handler


def test_sigint_handler_exits():
    with pytest.raises(SystemExit):
        _sigint_handler(signal.SIGINT, None)
