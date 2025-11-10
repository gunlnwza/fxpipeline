import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from fxpipeline.core import CurrencyPair, make_pair
from fxpipeline.ingestion.data_request import ForexPriceRequest
from fxpipeline.ingestion.loaders import get_loader
from fxpipeline.ingestion.loaders.alpha_vantage import AlphaVantageForex
from fxpipeline.ingestion.loaders.massive import MassiveForex
from fxpipeline.ingestion.loaders.yfinance_wrapper import YFinanceForex


def test_get_loader():
    assert get_loader("alpha_vantage").__class__.__name__ == "AlphaVantageForex"
    assert get_loader("massive").__class__.__name__ == "MassiveForex"
    assert get_loader("yfinance").__class__.__name__ == "YFinanceForex"

    # must require 1 argument
    with pytest.raises(TypeError):
        get_loader()

    # wrong spelling, must be case-insensitive
    with pytest.raises(ValueError):
        get_loader("Alpha_vantage")


@patch("fxpipeline.ingestion.loaders.alpha_vantage.requests.get")
def test_alpha_vantage_download(mock_get):
    mock_get.return_value.ok = True
    mock_get.return_value.headers = {"Content-Type": "text/csv"}
    mock_get.return_value.text = \
        "timestamp,open,high,low,close\n" \
        "2024-01-03,3,3,3,3\n" \
        "2024-01-02,2,2,2,2\n" \
        "2024-01-01,1,1,1,1\n"  # Alpha Vantage gives most recent data at the top

    loader = AlphaVantageForex("api_key")
    req = ForexPriceRequest(
        make_pair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03")
        )
    df = loader.download(req)

    assert isinstance(df, pd.DataFrame)

    assert df.index.name == "timestamp"
    assert df.index.to_list() == [
        pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")
        ]

    assert list(df.columns) == ["open", "high", "low", "close"]
    assert len(df) == 3
    assert df.iloc[0].to_list() == [1, 1, 1, 1]
    assert df.iloc[1].to_list() == [2, 2, 2, 2]
    assert df.iloc[2].to_list() == [3, 3, 3, 3]


@patch("fxpipeline.ingestion.loaders.massive.RESTClient")
def test_massive_download(mock_restclient):
    # Mock the RESTClient instance
    mock_client = MagicMock()
    mock_restclient.return_value = mock_client

    # Fake aggregation data like Polygon would return
    fake_aggs = [
        {"timestamp": 1704067200000, "open": 1, "high": 1, "low": 1, "close": 1,
         "volume": 10, "vwap": 1, "transactions": 10, "otc": False},
        {"timestamp": 1704153600000, "open": 2, "high": 2, "low": 2, "close": 2,
         "volume": 20, "vwap": 2, "transactions": 20, "otc": False},
        {"timestamp": 1704240000000, "open": 3, "high": 3, "low": 3, "close": 3,
         "volume": 30, "vwap": 3, "transactions": 30, "otc": False}
    ]
    mock_client.list_aggs.return_value = iter(fake_aggs)  # ← key part: iterable generator

    loader = MassiveForex("api_key")
    req = ForexPriceRequest(
        make_pair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03")
        )
    df = loader.download(req)

    assert isinstance(df, pd.DataFrame)

    assert df.index.name == "timestamp"
    assert df.index.to_list() == [
        pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")
        ]

    assert list(df.columns) == ["open", "high", "low", "close", "volume", "vwap"]
    assert len(df) == 3
    assert df.iloc[0].to_list() == [1, 1, 1, 1, 10, 1]
    assert df.iloc[1].to_list() == [2, 2, 2, 2, 20, 2]
    assert df.iloc[2].to_list() == [3, 3, 3, 3, 30, 3]


def _assert_clean_yfinance_df(df):
    assert isinstance(df, pd.DataFrame)

    assert df.index.name == "timestamp"
    assert df.index.to_list() == [
        pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")
        ]

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 3


@patch("fxpipeline.ingestion.loaders.yfinance_wrapper.yf.download")
def test_yfinance_download(mock_download):
    df = pd.DataFrame({
        "Close": [1, 2, 3],
        "High": [1, 2, 3],
        "Low": [1, 2, 3],
        "Open": [1, 2, 3],
        "Volume": [10, 20, 30]
    }, index=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")])

    df.index.name = "Date"
    sym = "ABCDEF=X"
    columns = [("Close", sym), ("High", sym), ("Low", sym), ("Open", sym), ("Volume", sym)]
    df.columns = pd.MultiIndex.from_tuples(columns)
    df.columns.names = ["Price", "Ticker"]

    mock_download.return_value = df

    loader = YFinanceForex()
    req = ForexPriceRequest(
        make_pair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03")
        )
    df = loader.download(req)

    _assert_clean_yfinance_df(df)
    assert df.iloc[0].to_list() == [1, 1, 1, 1, 10]
    assert df.iloc[1].to_list() == [2, 2, 2, 2, 20]
    assert df.iloc[2].to_list() == [3, 3, 3, 3, 30]


@patch("fxpipeline.ingestion.loaders.yfinance_wrapper.yf.download")
def test_yfinance_batch_download(mock_download):
    df = pd.DataFrame({
        "Close_1": [1, 2, 3],
        "High_1": [1, 2, 3],
        "Low_1": [1, 2, 3],
        "Open_1": [1, 2, 3],
        "Volume_1": [100, 200, 300],
        "Close_2": [10, 20, 30],
        "High_2": [10, 20, 30],
        "Low_2": [10, 20, 30],
        "Open_2": [10, 20, 30],
        "Volume_2": [100, 200, 300]
    }, index=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")])

    df.index.name = "Date"
    columns = [
        ("ABCDEF=X", "Open"), ("ABCDEF=X", "High"), ("ABCDEF=X", "Low"), ("ABCDEF=X", "Close"),
        ("ABCDEF=X", "Volume"),
        ("ABCXYZ=X", "Open"), ("ABCXYZ=X", "High"), ("ABCXYZ=X", "Low"), ("ABCXYZ=X", "Close"),
        ("ABCXYZ=X", "Volume")
        ]
    df.columns = pd.MultiIndex.from_tuples(columns)
    df.columns.names = ["Ticker", "Price"]

    mock_download.return_value = df

    loader = YFinanceForex()
    reqs = [
        ForexPriceRequest(
            make_pair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03")
        ),
        ForexPriceRequest(
            make_pair("ABCXYZ"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03")
        )
    ]
    lst = loader.batch_download(reqs)

    assert type(lst) == list
    assert len(lst) == 2
    assert isinstance(lst[0], pd.DataFrame)
    assert isinstance(lst[1], pd.DataFrame)

    _assert_clean_yfinance_df(lst[0])
    _assert_clean_yfinance_df(lst[1])
