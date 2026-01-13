from fxpipeline.simulation import Simulation


def run():
    sim = Simulation()
    while not sim.terminated:
        sim.next()


def register_simulate(subparsers):
    parser = subparsers.add_parser("simulate", help="Simulate")
    parser.add_argument("ticker", default="EURUSD", help="ticker to backtest on")
    parser.add_argument("-s", "--source", default="alpha_vantage", help="data source")
    parser.add_argument("--start", help="start date")
    parser.add_argument("--end", help="end date")

    parser.set_defaults(func=run)
