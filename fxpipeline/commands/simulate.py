import time

import math

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from fxpipeline.ingestion import load_forex_prices
from fxpipeline.simulation import Simulation
from fxpipeline.strategies.registry import create_strategy, STRATEGIES

# TODO: refactor!


def make_layout():
    layout = Layout(name="root")

    layout.split_column(
        Layout(name="header", size=1),  # Needed for correct rendering in VS Code terminal
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="left", size=35),
        Layout(name="positions", size=75),
    )
    layout["left"].split_column(
        Layout(name="price"),
        Layout(name="stats")
    )

    layout["header"].update("")
    return layout


def update_layout(layout, sim):
    layout["price"].update(Panel(price_table(sim), title="Price"))
    layout["stats"].update(Panel(stats(sim), title="Stats"))
    layout["positions"].update(Panel(positions(sim), title="Positions"))


def price_table(sim):
    table = Table(show_header=False)
    table.add_column("Key")
    table.add_column("Value")

    row = sim.ohlcv.iloc[sim.i]
    table.add_row("Index", str(sim.i))
    table.add_row("Date", str(sim.ohlcv.index[sim.i]))
    table.add_row("Open", f"{row.open:.4f}")
    table.add_row("High", f"{row.high:.4f}")
    table.add_row("Low", f"{row.low:.4f}")
    table.add_row("Close", f"{row.close:.4f}")

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
    table = Table(
        expand=True,
        show_header=True,
    )

    table.add_column("Symbol", width=6, no_wrap=True)
    table.add_column("Side", width=4, no_wrap=True)
    table.add_column("Entry", width=10, justify="right", no_wrap=True)
    table.add_column("SL", width=10, justify="right", no_wrap=True)
    table.add_column("TP", width=10, justify="right", no_wrap=True)
    table.add_column("PnL", width=10, justify="right", no_wrap=True)

    for order in sim.orders:
        if order.closed:
            continue

        side_color = "blue" if order.side == "buy" else "red"
        pnl_color = "blue" if order.pnl(sim.price) >= 0 else "red"
        table.add_row(
            sim.ticker,  # TODO: order must have ticker attr, and not sim
            f"[{side_color}]{order.side}[/{side_color}]",
            f"{order.open_price:.{sim.pip_digits}f}",
            f"{order.sl:.{sim.pip_digits}f}",
            f"{order.tp:.{sim.pip_digits}f}",
            f"[{pnl_color}]{order.pnl(sim.price):.{sim.pip_digits}f}[/{pnl_color}]"
        )

    return table


def run(args):
    data = load_forex_prices(args.ticker, args.source, args.start, args.end)
    sim = Simulation(data.df, args.ticker, round(math.log10(1 / data.pair.pip)))   # TODO: make pip a class???
    strategy = create_strategy(args.strategy)

    layout = make_layout()
    update_layout(layout, sim)

    with Live(layout, refresh_per_second=10) as live:
        while not sim.terminated:
            strategy.act(sim)  # TODO: have an intermediate interface data structure
            sim.next()

            if not args.dry:
                update_layout(layout, sim)
                time.sleep(args.time)

        update_layout(layout, sim)


def register_simulate(subparsers):
    parser = subparsers.add_parser("simulate", help="Simulate")
    parser.add_argument("ticker", nargs="?", default="EURUSD", help="ticker to backtest on")
    parser.add_argument("strategy", choices=STRATEGIES.keys(), nargs="?", default="random_trade", help="name of strategy to backtest on")
    parser.add_argument("-s", "--source", default="alpha_vantage", help="data source")
    parser.add_argument("--start", default="2025-01-01", help="start date")
    parser.add_argument("--end", help="end date")
    parser.add_argument("-t", "--time", type=float, default=0.1, help="time per candle")
    parser.add_argument("-d", "--dry", action="store_true", help="turn off animation")

    parser.set_defaults(func=run)
