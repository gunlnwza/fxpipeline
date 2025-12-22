from unittest.mock import patch, MagicMock

import pandas as pd

from fxpipeline.core import make_pair
from fxpipeline.ingestion.loader import MassiveForex


@patch("fxpipeline.ingestion.loader.massive.RESTClient")
def test_massive_download(mock_restclient):
    # Mock the RESTClient instance
    mock_client = MagicMock()
    mock_restclient.return_value = mock_client

    # Fake aggregation data like Polygon would return
    fake_aggs = [
        {
            "timestamp": 1735689600000,
            "open": 1,
            "high": 2,
            "low": 3,
            "close": 4,
            "volume": 10,
            "vwap": 5,
            "transactions": 6,
            "otc": 7,
        },
        {
            "timestamp": 1735776000000,
            "open": 11,
            "high": 12,
            "low": 13,
            "close": 14,
            "volume": 20,
            "vwap": 15,
            "transactions": 16,
            "otc": 17,
        },
        {
            "timestamp": 1735862400000,
            "open": 21,
            "high": 22,
            "low": 23,
            "close": 24,
            "volume": 30,
            "vwap": 25,
            "transactions": 26,
            "otc": 27,
        },
    ]
    mock_client.list_aggs.return_value = iter(
        fake_aggs
    )  # ← key part: iterable generator

    loader = MassiveForex(None)
    pair = make_pair("ABCDEF")
    data = loader.download(pair, pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-03"))

    assert data.pair == pair
    assert data.pair is not pair

    assert data.source == "massive"

    expected = pd.DataFrame(
        [[1, 2, 3, 4, 10], [11, 12, 13, 14, 20], [21, 22, 23, 24, 30]],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.Index(
            [pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="timestamp"
        ),
    )
    pd.testing.assert_frame_equal(data.df, expected)
