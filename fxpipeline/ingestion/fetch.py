import logging

import pandas as pd

from rich.console import Console
from rich.live import Live
from rich.status import Status

from .factory import get_loader, get_database
from .parse import parse_pairs, parse_source, parse_start_end, capitalize_source
from .base import NotDownloadedError, APIError
from ..core import ForexPrices, CurrencyPair
from ..utils import Stopwatch

logger = logging.getLogger(__file__)


def _fetch_single_pair(pair, source, start, end, db, loader):
    if db.have(pair, source, start, end):
        return "cached", None

    timer = Stopwatch()
    data = loader.download(pair, start, end)
    db.save(data)
    return "downloaded", timer


def print_pair_result(console, pair, result, timer: Stopwatch):
    if result == "cached":
        console.print(f"[bold]{pair}[/]: [green]Cached[/]")

    elif result == "downloaded":
        console.print(f"[bold]{pair}[/]: [green]Downloaded[/] in [not bold cyan]{timer.time:.1f}s[/]")
    
    elif isinstance(result, (NotDownloadedError, APIError)):
        console.print(f"[bold]{pair}: [red]{result}[/]")

    else:
        console.print(f"[bold]{pair}[/]: {result}")


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
    console = Console()
    status = Status("", spinner="dots")

    timer = Stopwatch()
    downloaded = 0

    pairs = parse_pairs(pairs)
    source = parse_source(source)
    start, end = parse_start_end(start, end, days=30)
    db = get_database("sqlite")
    loader = get_loader(source)
    console.print(f"[bold green]Fetching Forex Prices[/] | "
                  f"{capitalize_source(source)} | "
                  f"[not bold cyan]{start.date()} → {end.date()}[/]\n")

    with Live(status, console=console, refresh_per_second=10, transient=True):
        for pair in pairs:
            status.update(f"[bold]{pair}[/]: Downloading")
            try:
                result, fetch_timer = _fetch_single_pair(pair, source, start, end, db, loader)
            except (NotDownloadedError, APIError) as e:
                result, fetch_timer = e, None
            if result == "downloaded":
                downloaded += 1
            print_pair_result(console, pair, result, fetch_timer)

    db.close()
    console.print(f"\n[bold {"green" if downloaded > 0 else "default"}]{downloaded} pairs downloaded[/] | "
                  f"[green]Completed[/] in [not bold cyan]{timer.time:.1f}s[/]")


def load_forex_prices(
    pairs: str | CurrencyPair | list[str | CurrencyPair],
    source: str = "alpha_vantage",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> ForexPrices | list[ForexPrices]:
    """Load prices from local SQLite cache"""
    start, end = parse_start_end(start, end)

    db = get_database("sqlite")
    res = [db.load(pair, source, start, end) for pair in parse_pairs(pairs)]
    db.close()

    if isinstance(pairs, (str, CurrencyPair)):
        return res[0]
    return res
