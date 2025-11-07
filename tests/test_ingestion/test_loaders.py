import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from fxpipeline.ingestion.data import ForexPriceRequest, CurrencyPair
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
        l = get_loader()

    # wrong spelling, must be case-insensitive
    with pytest.raises(ValueError):
        l = get_loader("Alpha_vantage")


@patch("fxpipeline.ingestion.loaders.alpha_vantage.requests.get")
def test_alpha_vantage_download(mock_get):
    mock_get.return_value.ok = True
    mock_get.return_value.headers = {"Content-Type": "text/csv"}
    mock_get.return_value.text = "timestamp,open,high,low,close\n2024-01-01,1,2,0,1.5"

    loader = AlphaVantageForex("api_key")
    req = ForexPriceRequest(CurrencyPair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))
    df = loader.download(req)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "timestamp"
    assert list(df.columns) == ["open", "high", "low", "close"]
    assert len(df) == 1


@patch("fxpipeline.ingestion.loaders.massive.RESTClient")
def test_massive_download(mock_restclient):
    # Mock the RESTClient instance
    mock_client = MagicMock()
    mock_restclient.return_value = mock_client

    # Fake aggregation data like Polygon would return
    fake_aggs = [
        {"timestamp": 1704067200000, "open": 1.0, "high": 1.2, "low": 0.9, "close": 1.1, "volume": 42, "vwap": 1.0, "transactions": 5, "otc": False},
        {"timestamp": 1704153600000, "open": 1.1, "high": 1.3, "low": 1.0, "close": 1.2, "volume": 42, "vwap": 1.0, "transactions": 6, "otc": False},
    ]
    mock_client.list_aggs.return_value = iter(fake_aggs)  # ← key part: iterable generator

    loader = MassiveForex("api_key")
    req = ForexPriceRequest(CurrencyPair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))
    df = loader.download(req)

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["open", "high", "low", "close", "volume", "vwap"]
    assert df.index.name == "timestamp"
    assert len(df) == 2



@patch("fxpipeline.ingestion.loaders.yfinance_wrapper.yf.download")
def test_yfinance_download(mock_download):
    df = pd.DataFrame({
        "Close": [1, 2, 3],
        "High": [1, 2, 3],
        "Low": [1, 2, 3],
        "Open": [1, 2, 3],
        "Volume": [1, 2, 3]
    }, index=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")])

    df.index.name = "Date"
    sym = "ABCDEF=X"
    columns = [("Close", sym), ("High", sym), ("Low", sym), ("Open", sym), ("Volume", sym)]
    df.columns = pd.MultiIndex.from_tuples(columns)
    df.columns.names = ["Price", "Ticker"]

    mock_download.return_value = df

    loader = YFinanceForex()
    req = ForexPriceRequest(CurrencyPair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))
    df = loader.download(req)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "timestamp"
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 3
