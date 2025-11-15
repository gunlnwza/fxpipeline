from unittest.mock import patch, MagicMock

import pandas as pd

from fxpipeline.ingestion.loaders import MassiveForex


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

    loader = MassiveForex(None)
    df = loader.download("ABCDEF", pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))

    assert isinstance(df, pd.DataFrame)

    assert df.index.name == "timestamp"
    assert df.index.to_list() == [
        pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")
        ]

    assert list(df.columns) == ["open", "high", "low", "close", "volume", "vwap"]
    assert len(df) == 3
    assert df.iloc[0].to_list() == 
    assert df.iloc[1].to_list() == 
    assert df.iloc[2].to_list() == 

    expected = pd.DataFrame([
            [1, 1, 1, 1, 10, 1],
            [2, 2, 2, 2, 20, 2],
            [3, 3, 3, 3, 30, 3]
        ],
        columns = ["open", "high", "low", "close", "volume"],
        index=pd.Index([pd.Timestamp(f"2024-01-0{i}") for i in (1, 2, 3)], name="timestamp")
    )
    pd.testing.assert_frame_equal(df, expected)
