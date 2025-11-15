from unittest.mock import patch

import pandas as pd

from fxpipeline.core import make_pair
from fxpipeline.ingestion.loaders import YFinanceForex


@patch("fxpipeline.ingestion.loaders.yfinance_wrapper.yf.download")
def test_yfinance_download(mock_download):
    cols = ["Close", "High", "Low", "Open", "Volume"]
    df = pd.DataFrame([
            [1, 1, 1, 1, 10],
            [2, 2, 2, 2, 20],
            [3, 3, 3, 3, 30]
        ],
        columns=cols,
        index=pd.Index([pd.Timestamp(f"2024-01-0{i}") for i in (1, 2, 3)], name="Date")
    )
    df.columns = pd.MultiIndex.from_tuples([(col, "ABCDEF=X") for col in cols])
    df.columns.names = ["Price", "Ticker"]

    mock_download.return_value = df

    loader = YFinanceForex()
    df = loader.download(None, pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))

    expected = pd.DataFrame([
            [1, 1, 1, 1, 10],
            [2, 2, 2, 2, 20],
            [3, 3, 3, 3, 30]
        ],
        columns = ["open", "high", "low", "close", "volume"],
        index=pd.Index([pd.Timestamp(f"2024-01-0{i}") for i in (1, 2, 3)], name="timestamp")
    )
    pd.testing.assert_frame_equal(df, expected)



# @patch("fxpipeline.ingestion.loaders.yfinance_wrapper.yf.download")
# def test_yfinance_batch_download(mock_download):
#     df = pd.DataFrame({
#             "Close_1": [1, 2, 3],
#             "High_1": [1, 2, 3],
#             "Low_1": [1, 2, 3],
#             "Open_1": [1, 2, 3],
#             "Volume_1": [100, 200, 300],
#             "Close_2": [10, 20, 30],
#             "High_2": [10, 20, 30],
#             "Low_2": [10, 20, 30],
#             "Open_2": [10, 20, 30],
#             "Volume_2": [100, 200, 300]
#         }, index=pd.Index([pd.Timestamp(f"2024-01-0{i}") for i in (1, 2, 3)], name="Date")
#     )

#     df.index.name = "Date"
#     columns = [
#         ("ABCDEF=X", "Open"), ("ABCDEF=X", "High"), ("ABCDEF=X", "Low"), ("ABCDEF=X", "Close"),
#         ("ABCDEF=X", "Volume"),
#         ("ABCXYZ=X", "Open"), ("ABCXYZ=X", "High"), ("ABCXYZ=X", "Low"), ("ABCXYZ=X", "Close"),
#         ("ABCXYZ=X", "Volume")
#         ]
#     df.columns = pd.MultiIndex.from_tuples(columns)
#     df.columns.names = ["Ticker", "Price"]

#     mock_download.return_value = df

#     loader = YFinanceForex()
#     lst = loader.batch_download(
#         list(map(make_pair, ["ABCDEF", "ABCXYZ"])),
#         pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03")
#     )

#     assert isinstance(lst, list)
#     assert len(lst) == 2
#     assert isinstance(lst[0], pd.DataFrame)
#     assert isinstance(lst[1], pd.DataFrame)

#     pd.testing.assert_frame_equal(lst[0], )
#     pd.testing.assert_frame_equal(lst[1], )
