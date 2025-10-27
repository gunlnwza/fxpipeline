import time


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
