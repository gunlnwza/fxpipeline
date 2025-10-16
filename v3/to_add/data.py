from dataclasses import dataclass

import pandas as pd


@dataclass
class Ticker:
    from_symbol: str
    to_symbol: str

    @property
    def str(self) -> str:
        return f"{self.from_symbol}{self.to_symbol}"


def get_ticker(ticker: str) -> Ticker:
    assert len(ticker) == 6 and ticker.isupper() and ticker.isalpha()
    from_symbol = ticker[:3]
    to_symbol = ticker[3:]
    return Ticker(from_symbol, to_symbol)


@dataclass
class Timeframe:
    length: int
    unit: str

    @property
    def str(self) -> str:
        return f"{self.length}{self.unit}"


def get_timeframe(timeframe: str) -> Timeframe:
    length = int(timeframe[0])
    unit = timeframe[1]
    assert unit in "mhDMW"
    tf = Timeframe(length, unit)
    assert tf.str in ("1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M")
    return tf


@dataclass
class PriceMetaData:
    ticker: Ticker
    timeframe: Timeframe

    @property
    def str(self) -> str:
        return f"{self.ticker.str}_{self.timeframe.str}"


@dataclass
class Data:
    df: pd.DataFrame
    metadata: PriceMetaData
