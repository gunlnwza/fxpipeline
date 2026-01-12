import pandas as pd


def extract_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day"] = df.index.day

    df = df.reset_index(drop=True)
    return df
