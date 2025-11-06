import time


class Stopwatch:
    def __init__(self):
        self.start()

    def start(self):
        self._start = time.perf_counter()
        self._stop = None

    def stop(self):
        self._stop = time.perf_counter()

    @property
    def time(self):
        if self._stop:
            return self._stop - self._start
        else:
            return time.perf_counter() - self._start
