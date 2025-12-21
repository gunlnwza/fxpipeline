import sys
import signal


def _sigint_handler(sig, frame):
    print()
    sys.exit(0)


def handle_sigint():
    signal.signal(signal.SIGINT, _sigint_handler)
