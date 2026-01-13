import time

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from fxpipeline.ingestion import load_forex_prices
from fxpipeline.simulation import Simulation


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
    table.add_column("Open")
    table.add_column("High")
    table.add_column("Low")
    table.add_column("Close")

    row = sim.ohlcv.iloc[sim.i]
    table.add_row(
        str(sim.i),
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

    # table.add_row("Step", str(sim.i))
    # table.add_row("Terminated", str(sim.terminated))
    # table.add_row("Rows", str(len(sim.ohlcv)))

    table.add_row("Win pips", None)
    table.add_row("Loss pips", None)
    table.add_row("Total pips", None)

    return table


def positions(sim):
    table = Table()

    table.add_column("Symbol")
    table.add_column("Side")
    table.add_column("Size")
    table.add_column("PnL")

    # Placeholder until real position tracking exists
    table.add_row("EURUSD", "FLAT", "0", "0.0")

    return table


def run(args):
    data = load_forex_prices(args.ticker, args.source, args.start, args.end)
    sim = Simulation(data.df)

    layout = make_layout()
    update_layout(layout, sim)

    with Live(layout, refresh_per_second=10) as live:
        while not sim.terminated:
            sim.next()
            if not args.dry:
                update_layout(layout, sim)
                time.sleep(0.1)
        update_layout(layout, sim)


def register_simulate(subparsers):
    parser = subparsers.add_parser("simulate", help="Simulate")
    parser.add_argument("ticker", nargs="?", default="EURUSD", help="ticker to backtest on")
    parser.add_argument("-s", "--source", default="alpha_vantage", help="data source")
    parser.add_argument("--start", default="2025-01-01", help="start date")
    parser.add_argument("--end", help="end date")
    parser.add_argument("-d", "--dry", action="store_true", help="turn off animation")

    parser.set_defaults(func=run)
