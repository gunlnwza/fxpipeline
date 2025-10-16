from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class PricePoint:
    def __init__(self, index: int, price: float):
        self.index = index
        self.price = price

    def __repr__(self) -> str:
        return f"({self.index}, {self.price})"


class TimeHorizonDataFrame:
    """
    Wrapper for DataFrame that prevents peeking into future rows.
    Meant for backtesting: only allows access up to the current timestep.
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data.reset_index(drop=True)
        self.current_idx = 0
    
    def __str__(self):
        return self.data.iloc[:self.current_idx].__str__()

    @property
    def n(self):
        """Number of rows"""
        return len(self.data)

    def next(self):
        """Advance to the next row."""
        if self.current_idx > len(self.data) - 1:
            raise StopIteration("Reached end of data")
        self.current_idx += 1

    def view(self):
        """Return data up to current time"""
        return self.data.iloc[:self.current_idx + 1]

    def tail(self, n: int = 5):
        """Get last n rows"""
        if n <= 0:
            raise ValueError("n must be positive")
        if self.current_idx < self.n:  # TODO implement to not use view(), because chain indexing is bad
            return self.view()
        else:
            return self.view().iloc[-n:]

    def current_point(self):  # TODO: move to SimulationData (wrap TimeHorizonDataFrame)
        """Return current point."""
        index = min(self.current_idx, self.n - 1)
        return PricePoint(index, self.data.iloc[index, 0])


    # DEPRECATED
    # def get(self, i: int):  # TODO: might delete
    #     """Unsafe: use with caution; allows specific historical access."""
    #     if i > self._current_idx:
    #         raise IndexError("Trying to access future data")
    #     return self.data.iloc[i]

    # def reset(self):
    #     """Reset the time horizon"""
    #     self._current_idx = 0
