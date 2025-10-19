import os

from dotenv import load_dotenv

# from fxpipeline.data.yahoo_finance_data import YahooFinanceLoader
from polygon_data import PolygonLoader

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", type=str)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()

    load_dotenv("../../.env")
    loader = PolygonLoader(os.getenv("POLYGON_API_KEY"))
    # prices = loader.load(args.ticker, args.start, args.end)
    prices = loader.load(args.ticker)
    print(prices)
