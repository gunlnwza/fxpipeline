from yahoo_finance import YahooFinanceLoader

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", type=str)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()

    loader = YahooFinanceLoader()
    prices = loader.load(args.ticker, args.start, args.end)
    print(prices)
