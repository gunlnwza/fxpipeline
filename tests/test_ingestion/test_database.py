import os
import tempfile

import pandas as pd

from fxpipeline.core import ForexPrice, make_pair
from fxpipeline.ingestion.database import TextBasedDatabase


def test_textbased_database_save_and_load():
    with tempfile.TemporaryDirectory() as tempdir:
        db = TextBasedDatabase(tempdir)

        pair = make_pair("USDJPY")
        source = "test_source"

        data = ForexPrice(
            pair=pair,
            source=source,
            df=pd.DataFrame(
                {"open": [1.0, 1.1], "close": [1.2, 1.3]},
                index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
            )
        )

        db.save(data, source)
        assert db.have(pair, source)
        assert db.is_fresh(pair, source)

        loaded = db.load(pair, source)
        pd.testing.assert_frame_equal(data.df, loaded.df)
