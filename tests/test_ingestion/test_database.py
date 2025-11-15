import pandas as pd
import pytest

from fxpipeline.core import ForexPrice, make_pair
from fxpipeline.ingestion.database import SQLiteDatabase

"""
Database Jobs
- Insert price
- Store price (Alpha Vantage, Massive, yfinance) (All loaders yield same schema)
- Load price
- Fetch last price
- Fetch last timestamp
"""

@pytest.fixture
def pair():
    return make_pair("ABCDEF")


@pytest.fixture
def alpha_vantage_data() -> ForexPrice:
    df = pd.DataFrame([
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
            [11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20],
            [21, 22, 23, 24, 25]
        ],
        columns=["open", "high", "low", "close"],
        index=["2025-10-30", "2025-10-31", "2025-11-03", "2025-11-04", "2025-11-05"]
    )
    df.index.name = "timestamp"
    return ForexPrice(make_pair("EURUSD", "alpha_vantage"), df)


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


def test_save_and_load(db, data, pair):
    db.save(data)

    loaded_data = db.load(pair)
    assert loaded_data.pair == pair
    pd.testing.assert_frame_equal(loaded_data.df, data.df, rtol=1e-6, atol=1e-6)

    assert loaded_data.pair == data.pair
    assert loaded_data.pair is not data.pair


def test_last_value(populated_db, pair):
    assert populated_db.last_price(pair) == 24
    assert populated_db.last_timestamp(pair) == pd.Timestamp("2024-01-05")
