from dataclasses import dataclass

import numpy as np
import pandas as pd

from .currency import CurrencyPair


@dataclass
class ForexPrices:
    pair: CurrencyPair
    source: str
    df: pd.DataFrame
    # timeframe: ???

    @property
    def ticker(self):
        return self.pair.ticker

    def copy(self):
        return ForexPrices(self.pair, self.source, self.df.copy())

    def __len__(self):
        return len(self.df)


@dataclass
class PricePoint:
    timestamp: pd.Timestamp
    price: float


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: int

    @classmethod
    def from_array(cls, arr):
        return cls(*arr)
    
    @property
    def height(self) -> float:
        """
        Range of the candle
        - Always positive
        """
        return self.high - self.low
    
    @property
    def top_wick(self) -> float:
        """
        Size of top wick
        - Always positive
        """
        return self.high - max(self.open, self.close)
    
    @property
    def body(self) -> float:
        """
        Size of the body
        - (+) is a green candle
        - (-) is a red candle 
        """
        return self.close - self.open
    
    @property
    def bottom_wick(self) -> float:
        """
        Size of bottom wick
        - Always positive
        """
        return min(self.open, self.close) - self.low


@dataclass
class CandlesWindow:
    pair: CurrencyPair
    ohlcv: np.ndarray

    def __post_init__(self):
        assert len(self.ohlcv[0]) == 5

    @property
    def price(self):
        return self.ohlcv[-1, 3]

    def append(self, ohlcv_row):
        self.ohlcv[:-1] = self.ohlcv[1:]
        self.ohlcv[-1] = ohlcv_row

    def __getitem__(self, i: int) -> np.ndarray:
        return self.ohlcv[i]

    def candle(self, i: int) -> Candle:
        return Candle.from_array(self.ohlcv[i])
