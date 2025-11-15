from unittest.mock import patch

import pandas as pd

from fxpipeline.ingestion.loaders import YFinanceForex


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
    df = loader.download("ABCDEF", pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))

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
    lst = loader.batch_download(["ABCDEF", "ABCXYZ"],
                                pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))

    assert isinstance(lst, list)
    assert len(lst) == 2
    assert isinstance(lst[0], pd.DataFrame)
    assert isinstance(lst[1], pd.DataFrame)

    _assert_clean_yfinance_df(lst[0])
    _assert_clean_yfinance_df(lst[1])
