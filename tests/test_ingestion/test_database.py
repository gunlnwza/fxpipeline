import pandas as pd
import pytest

from fxpipeline.core import ForexPrice, make_pair
from fxpipeline.ingestion.database import SQLiteDatabase

"""
Database Jobs
- Insert price
- Store price (Alpha Vantage, Massive, yfinance)
- Load price
- Fetch last price
- Fetch last timestamp
"""


@pytest.fixture
def alpha_vantage_data() -> ForexPrice:
    df = pd.DataFrame([
            [1.16, 1.1637, 1.1546, 1.1565],
            [1.1565, 1.1577, 1.152, 1.1534],
            [1.1534, 1.1541, 1.1504, 1.1518],
            [1.1519, 1.1533, 1.1472, 1.1482],
            [1.1483, 1.1497, 1.1468, 1.1491]
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

# @pytest.fixture
# def massive_data():
#     return pd.DataFrame()


# @pytest.fixture
# def yfinance_data():
#     return pd.DataFrame()


def test_source_alpha_vantage(db, alpha_vantage_data):
    data = alpha_vantage_data
    pair = data.pair

    db.save(data)

    loaded_data = db.load(pair)
    assert loaded_data.pair == pair
    pd.testing.assert_frame_equal(loaded_data.df, data.df, rtol=1e-6, atol=1e-6)

    assert db.last_price(pair) == pytest.approx(1.1491, rel=1e-6)
    assert db.last_timestamp(pair) == pd.to_datetime("2025-11-05")

    assert "ticker" not in data.df.columns


# def test_source_massive():
#     pass

# def test_source_yfinance():
#     pass


# conn.close()
