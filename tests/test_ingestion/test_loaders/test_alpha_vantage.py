from unittest.mock import patch

import pandas as pd

from fxpipeline.core.currency import make_pair
from fxpipeline.ingestion.loader import AlphaVantageForex


@patch("fxpipeline.ingestion.loader.alpha_vantage.requests.get")
def test_alpha_vantage_download(mock_get):
    mock_get.return_value.ok = True
    mock_get.return_value.headers = {"Content-Type": "text/csv"}
    mock_get.return_value.text = (
        "timestamp,open,high,low,close\n"
        "2025-01-03,9,10,11,12\n"
        "2025-01-02,5,6,7,8\n"
        "2025-01-01,1,2,3,4\n"
    )  # Alpha Vantage gives data in descending order

    loader = AlphaVantageForex("api_key")
    pair = make_pair("ABCDEF")
    data = loader.download(pair, pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-03"))

    assert data.pair == pair
    assert data.pair is not pair

    assert data.source == "alpha_vantage"

    expected = pd.DataFrame(
        [[1, 2, 3, 4, 0], [5, 6, 7, 8, 0], [9, 10, 11, 12, 0]],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.Index(
            [pd.Timestamp(f"2025-01-0{i}") for i in (1, 2, 3)], name="timestamp"
        ),
    )
    pd.testing.assert_frame_equal(data.df, expected)
