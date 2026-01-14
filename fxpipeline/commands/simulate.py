import time

import math
import random

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from fxpipeline.ingestion import load_forex_prices
from fxpipeline.simulation import Simulation

# TODO: refactor!


def make_layout():
    layout = Layout(name="root")

    layout.split_column(
        Layout(name="header", size=1),  # Needed for correct rendering in VS Code terminal
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="positions"),
    )
    layout["left"].split_column(
        Layout(name="price", size=9),
        Layout(name="stats")
    )

    layout["header"].update("")
    return layout


def update_layout(layout, sim):
    layout["price"].update(Panel(price_table(sim), title="Price"))
    layout["stats"].update(Panel(stats(sim), title="Stats"))
    layout["positions"].update(Panel(positions(sim), title="Positions"))


def price_table(sim):
    table = Table()

    table.add_column("Index")
    table.add_column("Date")
    table.add_column("Open")
    table.add_column("High")
    table.add_column("Low")
    table.add_column("Close")

    row = sim.ohlcv.iloc[sim.i]
    table.add_row(
        str(sim.i),
        str(sim.ohlcv.index[sim.i]),
        f"{row.open:.5f}",
        f"{row.high:.5f}",
        f"{row.low:.5f}",
        f"{row.close:.5f}",
    )
    return table


def stats(sim):
    table = Table(show_header=False)
    table.add_column("Key")
    table.add_column("Value")

    table.add_row("Win pips", str(sim.win_pips))
    table.add_row("Loss pips", str(sim.loss_pips))
    table.add_row("Total pips", str(sim.win_pips - sim.loss_pips))

    return table


def positions(sim):
    table = Table()

    table.add_column("Symbol", width=6)
    table.add_column("Side", width=4)
    table.add_column("Entry", ratio=1)
    table.add_column("SL", ratio=1)
    table.add_column("TP", ratio=1)
    table.add_column("PnL", ratio=1)

    # Placeholder until real position tracking exists
    for order in sim.orders:
        if order.closed:
            continue
        # TODO: order must have ticker attribute instead of sim
        table.add_row(*(
            [sim.ticker, order.side]
            + list(
                map(lambda x: str(round(x, sim.pip_digits)), [order.open_price, order.sl, order.tp, order.pnl(sim.price)])
            )
        ))

    return table


def run(args):
    data = load_forex_prices(args.ticker, args.source, args.start, args.end)
    sim = Simulation(data.df, args.ticker, round(math.log10(1 / data.pair.pip)))   # TODO: make pip a class???

    layout = make_layout()
    update_layout(layout, sim)

    with Live(layout, refresh_per_second=5) as live:
        while not sim.terminated:
            if random.random() < 0.2:
                row = sim.ohlcv.iloc[sim.i]
                o = row["open"]
                h = row["high"]
                l = row["low"]
                c = row["close"]
                body = c - o
                height = h - l

                if body > 0:
                    sim.open_buy(c + height, c - height, c + 3*height)
                else:
                    sim.open_sell(c - height, c + height, c - 3*height)

            sim.next()

            if not args.dry:
                update_layout(layout, sim)
                time.sleep(args.time)

        update_layout(layout, sim)


def register_simulate(subparsers):
    parser = subparsers.add_parser("simulate", help="Simulate")
    parser.add_argument("ticker", nargs="?", default="EURUSD", help="ticker to backtest on")
    parser.add_argument("-s", "--source", default="alpha_vantage", help="data source")
    parser.add_argument("--start", default="2025-01-01", help="start date")
    parser.add_argument("--end", help="end date")
    parser.add_argument("-t", "--time", type=float, default=0.1, help="time per candle")
    parser.add_argument("-d", "--dry", action="store_true", help="turn off animation")

    parser.set_defaults(func=run)
