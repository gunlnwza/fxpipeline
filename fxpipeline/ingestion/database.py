import logging
import sqlite3
from abc import ABC, abstractmethod

import pandas as pd

from ..core import ForexPrice, CurrencyPair

logger = logging.getLogger(__name__)


class ForexPriceDatabase(ABC):
    @abstractmethod
    def save(self, data: ForexPrice):
        """Save `data`, append to table, overwrite existing rows"""

    @abstractmethod
    def load(self, pair: CurrencyPair, source: str) -> ForexPrice:
        """Load all historical data of `pair`"""

    @abstractmethod
    def last_price(self, pair: CurrencyPair, source: str) -> float:
        """Get only last price of `pair`"""

    @abstractmethod
    def last_timestamp(self, pair: CurrencyPair, source: str) -> pd.Timestamp:
        """Get only last timestamp of `pair`"""

    @abstractmethod
    def have(self, pair: CurrencyPair, source: str,
             start: pd.Timestamp, end: pd.Timestamp) -> bool:
        """True if have `source`'s `pair` with datetimes [`start`, `end`]"""


class SQLiteDatabase(ForexPriceDatabase):
    def __init__(self, database: str):
        self.conn = sqlite3.connect(database)

    def open(self, database: str):
        self.conn = sqlite3.connect(database)

    def close(self):
        self.conn.close()
        self.conn = None

    def save(self, data: ForexPrice):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS Prices (
                    source TEXT,
                    ticker TEXT,
                    timestamp DATETIME,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INT,
                    PRIMARY KEY (source, ticker, timestamp) ON CONFLICT REPLACE
                );
                """)

            df = data.df.copy()
            df.reset_index(inplace=True)
            df["source"] = data.source
            df["ticker"] = data.pair.ticker
            df = df[["source", "ticker", "timestamp", "open", "high", "low", "close", "volume"]]
            df.to_sql("Prices", self.conn, if_exists="append", index=False)

    def load(self, pair: CurrencyPair, source: str) -> ForexPrice:
        df = pd.read_sql("""
            SELECT *
            FROM Prices
            WHERE source = ? AND ticker = ?;
            """, self.conn, params=(source, pair.ticker), index_col="timestamp", parse_dates=True)
        df.index = pd.to_datetime(df.index)
        df.drop(["source", "ticker"], axis=1, inplace=True)
        return ForexPrice(pair.copy(), source, df)

    def last_price(self, pair: CurrencyPair, source: str) -> float:
        cursor = self.conn.execute("""
            SELECT close
            FROM Prices
            WHERE source = ? AND ticker = ?
            ORDER BY timestamp DESC
            LIMIT 1;
            """, (source, pair.ticker))
        res = cursor.fetchone()
        return res[0] if res else None

    def last_timestamp(self, pair: CurrencyPair, source: str) -> pd.Timestamp:
        cursor = self.conn.execute("""
            SELECT timestamp
            FROM Prices
            WHERE source = ? AND ticker = ?
            ORDER BY timestamp DESC
            LIMIT 1;
            """, (source, pair.ticker))
        res = cursor.fetchone()
        return pd.Timestamp(res[0]) if res else None

    def have(self, pair: CurrencyPair, source: str,
             start: pd.Timestamp, end: pd.Timestamp) -> bool:
        cursor = self.conn.execute("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM Prices
            WHERE source = ? AND ticker = ?
            """, (source, pair.ticker))

        res = cursor.fetchone()
        min_time, max_time = res

        if min_time is None or max_time is None:
            return False  # no rows

        return pd.Timestamp(min_time) <= start and pd.Timestamp(max_time) >= end
