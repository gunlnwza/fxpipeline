import pandas as pd
import pytest

from fxpipeline.core import ForexPrice, make_pair
from fxpipeline.ingestion._OLD_database import SQLiteDatabase

"""
Database Jobs
- Insert price
- Store price (Alpha Vantage, Massive, yfinance)
- Load price
- Fetch last price
- Fetch last timestamp
"""

# conn = SQLiteDatabase(":memory:")
# usdjpy = make_pair("USDJPY")
# eurusd = make_pair("EURUSD")


@pytest.fixture
def alpha_vantage_df():
    return pd.DataFrame()  # declare with list


@pytest.fixture
def massive_df():
    return pd.DataFrame()


@pytest.fixture
def yfinance_df():
    return pd.DataFrame()


def test_source_alpha_vantage(alpha_vantage_df):
    with conn:
        # test insert
        pass

    # test fetch single df

    # test fetch last price


# def test_source_massive():
#     pass

# def test_source_yfinance():
#     pass


# conn.close()
