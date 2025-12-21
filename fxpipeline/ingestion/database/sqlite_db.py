import logging
import sqlite3
from pathlib import Path

import pandas as pd

from ..base import ForexPriceDatabase
from ...core import ForexPrice, CurrencyPair

logger = logging.getLogger(__name__)


class SQLiteDatabase(ForexPriceDatabase):
    def __init__(self, database: str):
        path = Path(database)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(database)
        self.db = database

        self._create_prices_table_if_not_exist()

    def _create_prices_table_if_not_exist(self):
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

    def open(self, database: str):
        self.conn = sqlite3.connect(database)

    def close(self):
        self.conn.close()
        self.conn = None

    def save(self, data: ForexPrice):
        df = data.df.copy()
        df.reset_index(inplace=True)
        df["source"] = data.source
        df["ticker"] = data.pair.ticker
        df = df[
            ["source", "ticker", "timestamp", "open", "high", "low", "close", "volume"]
        ]
        with self.conn:
            df.to_sql("Prices", self.conn, if_exists="append", index=False)
            logger.debug(f"Save {data.pair} to '{self.db}'")

    def load(
        self,
        pair: CurrencyPair,
        source: str,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
    ) -> ForexPrice:
        sql = """
            SELECT *
            FROM Prices
            WHERE source = ? AND ticker = ?
        """
        params = [source, pair.ticker]

        if start is not None:
            sql += " AND timestamp >= ?"
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))

        if end is not None:
            sql += " AND timestamp <= ?"
            params.append(end.strftime("%Y-%m-%d %H:%M:%S"))

        df = pd.read_sql(
            sql, self.conn, params=params, index_col="timestamp", parse_dates=True
        )
        df.index = pd.to_datetime(df.index)
        df.drop(["source", "ticker"], axis=1, inplace=True)
        return ForexPrice(pair.copy(), source, df)
    
    def have(
        self, pair: CurrencyPair, source: str, start: pd.Timestamp, end: pd.Timestamp
    ) -> bool:
        # adjust if tips are weekends
        while start.weekday() >= 5:
            start += pd.Timedelta(days=1)
        start = start.normalize()

        while end.weekday() >= 5:
            end -= pd.Timedelta(days=1)
        end = end.normalize()

        cursor = self.conn.execute(
            """
            SELECT MIN(timestamp), MAX(timestamp)
            FROM Prices
            WHERE source = ? AND ticker = ?
            """,
            (source, pair.ticker),
        )

        res = cursor.fetchone()
        min_time, max_time = res

        if min_time is None or max_time is None:
            return False  # no rows

        return pd.Timestamp(min_time) <= start and pd.Timestamp(max_time) >= end

    def last_price(self, pair: CurrencyPair, source: str) -> float:
        cursor = self.conn.execute(
            """
            SELECT close
            FROM Prices
            WHERE source = ? AND ticker = ?
            ORDER BY timestamp DESC
            LIMIT 1;
            """,
            (source, pair.ticker),
        )
        res = cursor.fetchone()
        return res[0] if res else None

    def last_timestamp(self, pair: CurrencyPair, source: str) -> pd.Timestamp:
        cursor = self.conn.execute(
            """
            SELECT timestamp
            FROM Prices
            WHERE source = ? AND ticker = ?
            ORDER BY timestamp DESC
            LIMIT 1;
            """,
            (source, pair.ticker),
        )
        res = cursor.fetchone()
        return pd.Timestamp(res[0]) if res else None
