import pandas as pd

from ..core import CurrencyPair, make_pair

DEFAULT_LOOKBACK_DAYS = 42000


def parse_pairs(pairs: str | CurrencyPair | list[str | CurrencyPair]) -> list[CurrencyPair]:
    if isinstance(pairs, (str, CurrencyPair)):
        return [make_pair(pairs)]
    else:
        res = []
        for pair in pairs:
            p = make_pair(pair)
            if p not in res:
                res.append(p)
        return res


def parse_source(source: str) -> str:
    """Fuzzy match `source`"""
    if source == "av":
        return "alpha_vantage"
    elif source == "yf":
        return "yfinance"
    elif source == "polygon":
        return "massive"
    return source


def capitalize_source(source: str) -> str:
    source = parse_source(source)
    if source == "alpha_vantage":
        return "Alpha Vantage"
    elif source == "massive":
        return "Massive"
    elif source == "yfinance":
        return "Yahoo Finance"


def parse_start_end(start=None, end=None, days=None):
    if days is None:
        days = DEFAULT_LOOKBACK_DAYS

    if end is None:
        end = pd.Timestamp.now() - pd.Timedelta(days=1)  # chosen because yesterday price is settled
    if start is None:
        start = end - pd.Timedelta(days=days)

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return start, end
