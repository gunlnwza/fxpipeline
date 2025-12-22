import pandas as pd
import pytest

from fxpipeline.core import ForexPrices, CurrencyPair, make_pair
from fxpipeline.ingestion.database.sqlite_db import SQLiteDatabase

"""
Database Jobs
- Insert price
- Store price (Alpha Vantage, Massive, yfinance) (All loaders yield same schema)
- Load price
- Fetch last price
- Fetch last timestamp
"""


@pytest.fixture
def pair() -> CurrencyPair:
    return make_pair("ABCDEF")


@pytest.fixture
def data(pair) -> ForexPrices:
    df = pd.DataFrame(
        [
            [1.0, 2.0, 3.0, 4.0, 5],
            [6.0, 7.0, 8.0, 9.0, 10],
            [11.0, 12.0, 13.0, 14.0, 15],
            [16.0, 17.0, 18.0, 19.0, 20],
            [21.0, 22.0, 23.0, 24.0, 25],
        ],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.Index(
            [pd.Timestamp(f"2025-01-0{i}") for i in range(1, 6)], name="timestamp"
        ),
    )
    return ForexPrices(pair, "source", df)


@pytest.fixture
def data_2(data) -> ForexPrices:
    data = data.copy()
    data.source = "source_2"
    return data


@pytest.fixture
def db():
    db = SQLiteDatabase(":memory:")
    yield db
    db.close()


@pytest.fixture
def populated_db(data):
    db = SQLiteDatabase(":memory:")
    db.save(data)
    yield db
    db.close()


def test_save_and_load(db, pair, data, data_2):
    db.save(data)
    db.save(data_2)

    loaded_data = db.load(pair, "source")
    assert loaded_data.pair == pair
    assert loaded_data.pair is not pair
    assert loaded_data.source == "source"
    pd.testing.assert_frame_equal(loaded_data.df, data.df, rtol=1e-6, atol=1e-6)

    loaded_data_2 = db.load(pair, "source_2")
    assert loaded_data_2.pair == data.pair
    assert loaded_data_2.pair is not data.pair
    assert loaded_data_2.source == "source_2"


def test_load_date_range(populated_db, pair):
    data = populated_db.load(
        pair, "source", start=pd.Timestamp("2025-01-02"), end=pd.Timestamp("2025-01-04")
    )
    assert data.df.index.to_list() == [pd.Timestamp(f"2025-01-0{i}") for i in (2, 3, 4)]


def test_last_value(populated_db, pair):
    assert populated_db.last_price(pair, "source") == 24
    assert populated_db.last_timestamp(pair, "source") == pd.Timestamp("2025-01-05")


def test_have(populated_db, pair):
    start = pd.Timestamp("2025-01-01")
    end = pd.Timestamp("2025-01-05")
    assert populated_db.have(pair, "source", start, end) is True

    end = pd.Timestamp("2025-01-06")
    assert populated_db.have(pair, "source", start, end) is False
