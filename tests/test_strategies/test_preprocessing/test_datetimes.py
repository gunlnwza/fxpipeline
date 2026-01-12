import pytest
import pandas as pd

from fxpipeline.strategies.preprocessing.datetimes import extract_timestamp


@pytest.fixture
def df():
    return pd.DataFrame(
        {"col": [1, 2, 3, 4, 5]},
        dtype="int32",
        index=pd.Index([pd.Timestamp(f"2025-01-0{i}") for i in range(1, 6)]),
    )


def test_extract_timestamp(df):
    extracted = extract_timestamp(df)
    assert extracted is not df

    expected = pd.DataFrame(
        {
            "col": [1, 2, 3, 4, 5],
            "year": [2025, 2025, 2025, 2025, 2025],
            "month": [1, 1, 1, 1, 1],
            "day": [1, 2, 3, 4, 5],
        },
        dtype="int32",
        index=[0, 1, 2, 3, 4],
    )
    pd.testing.assert_frame_equal(extracted, expected)
