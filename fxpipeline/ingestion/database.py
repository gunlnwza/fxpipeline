import logging
import sqlite3
from abc import ABC, abstractmethod

import pandas as pd

from ..core import ForexPrice, CurrencyPair

logger = logging.getLogger(__name__)


class ForexPriceDatabase(ABC):
    @abstractmethod
    def save(self, data: ForexPrice):
        """Save 'data', append to table, overwrite existing rows"""
        pass

    @abstractmethod
    def load(self, pair: CurrencyPair) -> ForexPrice:
        """Load all historical data of 'pair'"""
        pass

    @abstractmethod
    def last_price(self, pair: CurrencyPair) -> float:
        """Get only last price of 'pair'"""
        pass

    @abstractmethod
    def last_timestamp(self, pair: CurrencyPair) -> pd.Timestamp:
        """Get only last timestamp of 'pair"""
        pass


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
                """
            )

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
            """,
            conn, params=(source, pair.ticker), index_col="timestamp", parse_dates=True
        )
        df.drop(["source, ticker"], axis=1, inplace=True)
        return ForexPrice(pair.copy(), source, df)

    def last_price(self, pair: CurrencyPair) -> float:
        table = f"{pair.source}_prices"
        with self.conn as conn:
            last_price = pd.read_sql(f'''
                SELECT close FROM {table}
                WHERE ticker = "{pair.ticker}"
                ORDER BY timestamp DESC
                LIMIT 1;
                ''',
                conn
            )["close"].iloc[0]
        return last_price

    def last_timestamp(self, pair: CurrencyPair) -> pd.Timestamp:
        table = f"{pair.source}_prices"
        with self.conn as conn:
            last_timestamp = pd.read_sql(f'''
                SELECT timestamp
                FROM {table}
                WHERE ticker = "{pair.ticker}"
                ORDER BY timestamp DESC
                LIMIT 1;
                ''',
                conn
            )["timestamp"].iloc[0]
        return pd.Timestamp(last_timestamp)
