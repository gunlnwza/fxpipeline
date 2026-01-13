import os
import logging

import pandas as pd

from rich.console import Console
from rich.live import Live
from rich.status import Status

from .factory import get_loader, get_database
from ..core import ForexPrices, CurrencyPair, make_pair
from ..utils import Stopwatch

CACHES_PATH = os.getenv("CACHES_PATH")
DEFAULT_LOOKBACK_DAYS = 42000

logger = logging.getLogger(__file__)


def _convert_pairs(pairs: str | CurrencyPair | list[str | CurrencyPair]) -> list[CurrencyPair]:
    if isinstance(pairs, str) or isinstance(pairs, CurrencyPair):
        return [make_pair(pairs)]
    else:
        return [make_pair(p) for p in pairs]


def _convert_source(source: str) -> str:
    if source == "av":
        return "alpha_vantage"
    elif source == "yf":
        return "yfinance"
    elif source == "polygon":
        return "massive"
    return source

def _capitalize_source(source: str) -> str:
    if source == "alpha_vantage":
        return "Alpha Vantage"
    elif source == "massive":
        return "Massive"
    elif source == "yfinance":
        return "yfinance"

def _convert_start_end(start=None, end=None, days=None):
    if days is None:
        days = DEFAULT_LOOKBACK_DAYS

    if end is None:
        end = pd.Timestamp.now()
    if start is None:
        start = end - pd.Timedelta(days=days)

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return start, end


def fetch_forex_prices(
    pairs: str | CurrencyPair | list[str | CurrencyPair],
    source: str,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
):
    """
    Fetch prices from the internet and save to SQLite Cache.
    Ignore if already have the price.
    """
    pairs = _convert_pairs(pairs)
    source = _convert_source(source)
    start, end = _convert_start_end(start, end, days=30)
    
    console = Console()
    status = Status("", spinner="dots")

    db = get_database("sqlite")
    loader = get_loader(source)
    total_time = Stopwatch()
    downloaded = 0
    
    console.print(f"[bold green]Fetching Forex Prices[/] | {_capitalize_source(source)} | [not bold cyan]{start.date()} → {end.date()}[/]\n")
    with Live(status, console=console, refresh_per_second=10, transient=True):
        for pair in pairs:
            status.update(f"[bold]{pair}[/]: Downloading")
            if db.have(pair, source, start, end):
                console.print(f"[bold]{pair}[/]: [green]Cached[/]")
            else:
                download_time = Stopwatch()
                data = loader.download(pair, start, end)
                db.save(data)
                console.print(f"[bold]{pair}[/]: [green]Downloaded[/] in [not bold cyan]{download_time}s[/]")
                downloaded += 1
        status.update(" ")
    db.close()
    console.print(f"\n[bold default]{downloaded} pairs downloaded[/] | [green]Completed[/] in [not bold cyan]{total_time}s[/]")


def load_forex_prices(
    pairs: str | CurrencyPair | list[str | CurrencyPair],
    source: str = "alpha_vantage",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> ForexPrices | list[ForexPrices]:
    """Load prices from local SQLite cache"""
    start, end = _convert_start_end(start, end)

    db = get_database("sqlite")
    res = [db.load(pair, source, start, end) for pair in _convert_pairs(pairs)]
    db.close()

    if isinstance(pairs, str) or isinstance(pairs, CurrencyPair):
        return res[0]
    return res
