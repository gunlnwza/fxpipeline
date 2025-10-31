import pandas as pd

from .get_loader import get_loader


# TODO: currently Loaders are responsible for both downloading and loading, I hate that.
def load_forex_price(ticker: str, source: str = "alpha_vantage") -> pd.DataFrame:
    """
    Load existing price from cache 
    """
    loader = get_loader(source)
    try:
        df = loader.load_every_row(ticker)
        return df
    except FileNotFoundError as e:
        print("Error:", e)
        return None
