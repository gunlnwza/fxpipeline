from unittest.mock import patch

import pandas as pd

from fxpipeline.core.currency import make_pair
from fxpipeline.ingestion.loaders import AlphaVantageForex


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
    df = loader.download(make_pair("ABCDEF"), pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))

    assert isinstance(df, pd.DataFrame)
    expected = pd.DataFrame([
        [1, 1, 1, 1],
        [2, 2, 2, 2],
        [3, 3, 3, 3]
    ])
    pd.testing.assert_frame_equal(df, expected)
