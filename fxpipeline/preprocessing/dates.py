def separate_timestamp(df: pd.DataFrame):
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day"] = df.index.day
    df = df.reset_index(drop=True)
    return df
