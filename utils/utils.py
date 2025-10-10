import time
import argparse
import logging

from rich.console import Console
from rich.text import Text


class Stopwatch:
    def __init__(self):
        self.start()

    def start(self):
        self._start = time.time()
        self._stop = None

    def stop(self):
        self._stop = time.time()

    @property
    def time(self):
        if self._stop:
            return self._stop - self._start
        else:
            return time.time() - self._start


class PrettyLogger:
    EMOJIS = {
        "INFO": "ℹ️ ",
        "DEBUG": "🔍",
        "WARNING": "🚩",
        "ERROR": "💥",
        "CRITICAL": "🔥",
    }

    COLORS = {
        "INFO": "cyan",
        "DEBUG": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
    }

    def __init__(self, name="app"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.console = Console()

    def log(self, level, message):
        emoji = self.EMOJIS.get(level, "")
        color = self.COLORS.get(level, "white")
        text = Text(f"{level:<8} | {emoji} {message}", style=color)
        self.console.print(text)

    def info(self, msg): self.log("INFO", msg)
    def debug(self, msg): self.log("DEBUG", msg)
    def warning(self, msg): self.log("WARNING", msg)
    def error(self, msg): self.log("ERROR", msg)
    def critical(self, msg): self.log("CRITICAL", msg)


def get_base_parser():
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("ticker")
    base.add_argument("timeframe")
    return base
