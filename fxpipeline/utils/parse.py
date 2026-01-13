import pandas as pd
from itertools import combinations

from fxpipeline.core import make_pair, CurrencyPair


def parse_tickers(tickers: list[str]) -> list[CurrencyPair]:
    global_curs = ("EUR", "GBP", "AUD", "NZD", "CAD", "CHF", "JPY")

    if tickers[0] in ("major", "minor"):
        assert len(tickers) == 1, f"Invalid ticker list {tickers}"
    if tickers[0] == "major":
        return [make_pair(a + "USD") for a in global_curs]
    elif tickers[0] == "minor":
        return [make_pair(a + b) for a, b in combinations(global_curs, 2)]

    return [make_pair(t) for t in tickers]


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


def parse_start_end(start=None, end=None, default_lookback_days=None):
    if default_lookback_days is None:
        default_lookback_days = 36500

    if end is None:
        end = pd.Timestamp.now() - pd.Timedelta(days=1)  # chosen because yesterday price is settled
    if start is None:
        start = end - pd.Timedelta(days=default_lookback_days)

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return start, end
