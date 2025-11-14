import os
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

    def _create_alpha_vantage_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS alpha_vantage_prices (
            ticker TEXT,
            timestamp DATETIME,
            open REAL,
            high REAL,
            low REAL,
            close REAL
        );
        """)

    def _create_massive_table(self):
        self.conn.execute()

    def _create_yfinance_table(self):
        self.conn.execute()

    def save(self, data: ForexPrice):
        source = data.pair.source
        table = f"{source}_prices"
        df = data.df.copy()
        with self.conn:
            match source:
                case "alpha_vantage":
                    self._create_alpha_vantage_table()
                case "massive":
                    self._create_massive_table()
                case "yfinance":
                    self._create_yfinance_table()
                case _:
                    raise ValueError(f"Source '{source}' is not supported")
            df.reset_index(inplace=True)
            df.insert(0, "ticker", data.pair.ticker)
            df.to_sql(table, self.conn, if_exists="replace", index=False)

    def load(self, pair: CurrencyPair) -> ForexPrice:
        table = f"{pair.source}_prices"
        ticker = pair.ticker
        with self.conn as conn:
            df = pd.read_sql(f'''
                SELECT *
                FROM {table}
                WHERE ticker = "{ticker}";
                ''',
                conn, parse_dates=True, index_col="timestamp"
            )
        df.drop("ticker", axis=1, inplace=True)
        return ForexPrice(pair.copy(), df)

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
