from unittest.mock import patch

import pandas as pd

from fxpipeline.core import make_pair
from fxpipeline.ingestion.loader import YFinanceForex


@patch("fxpipeline.ingestion.loader.yfinance_wrapper.yf.download")
def test_yfinance_download(mock_download):
    # using group_by="ticker"
    cols = ["Open", "High", "Low", "Close", "Volume"]
    df = pd.DataFrame(
        [[1, 2, 3, 4, 10], [6, 7, 8, 9, 20], [11, 12, 13, 14, 30]],
        columns=pd.MultiIndex.from_tuples(
            [("ABCDEF=X", col) for col in cols], names=["Ticker", "Price"]
        ),
        index=pd.Index([pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="Date"),
    )

    mock_download.return_value = df

    loader = YFinanceForex()
    pair = make_pair("ABCDEF")
    data = loader.download(pair, pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-03"))

    assert data.pair == pair
    assert data.pair is not pair

    assert data.source == "yfinance"

    expected = pd.DataFrame(
        [[1, 2, 3, 4, 10], [6, 7, 8, 9, 20], [11, 12, 13, 14, 30]],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.Index(
            [pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="timestamp"
        ),
    )
    pd.testing.assert_frame_equal(data.df, expected)


@patch("fxpipeline.ingestion.loader.yfinance_wrapper.yf.download")
def test_yfinance_batch_download(mock_download):
    # using group_by="ticker"
    tickers = ["ABCDEF=X", "ABCXYZ=X"]
    cols = ["Open", "High", "Low", "Close", "Volume"]
    df = pd.DataFrame(
        [
            [1, 2, 3, 4, 100, 51, 52, 53, 54, 100],
            [6, 7, 8, 9, 200, 56, 57, 58, 59, 200],
            [11, 12, 13, 14, 300, 61, 62, 63, 64, 300],
        ],
        columns=pd.MultiIndex.from_tuples(
            [(ticker, col) for ticker in tickers for col in cols],
            names=["Ticker", "Price"],
        ),
        index=pd.Index([pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="Date"),
    )

    mock_download.return_value = df

    loader = YFinanceForex()
    pair_1 = make_pair("ABCDEF")
    pair_2 = make_pair("ABCXYZ")
    lst = loader.batch_download(
        [pair_1, pair_2], pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-03")
    )

    assert isinstance(lst, list)
    assert len(lst) == 2

    # lst[0]
    assert lst[0].pair == pair_1
    assert lst[0].pair is not pair_1

    assert lst[0].source == "yfinance"

    expected = pd.DataFrame(
        [[1, 2, 3, 4, 100], [6, 7, 8, 9, 200], [11, 12, 13, 14, 300]],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.Index(
            [pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="timestamp"
        ),
    )
    pd.testing.assert_frame_equal(lst[0].df, expected)

    # lst[1]
    assert lst[1].pair == pair_2
    assert lst[1].pair is not pair_2

    assert lst[1].source == "yfinance"

    expected = pd.DataFrame(
        [[51, 52, 53, 54, 100], [56, 57, 58, 59, 200], [61, 62, 63, 64, 300]],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.Index(
            [pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="timestamp"
        ),
    )
    pd.testing.assert_frame_equal(lst[1].df, expected)
