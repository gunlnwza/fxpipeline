from fxpipeline.core import make_pair


def test_major_currencies():
    tickers = [
        "EURGBP",
        "EURAUD",
        "EURNZD",
        "EURUSD",
        "EURCAD",
        "EURCHF",
        "EURJPY",
        "GBPAUD",
        "GBPNZD",
        "GBPUSD",
        "GBPCAD",
        "GBPCHF",
        "GBPJPY",
        "AUDNZD",
        "AUDUSD",
        "AUDCAD",
        "AUDCHF",
        "AUDJPY",
        "NZDUSD",
        "NZDCAD",
        "NZDCHF",
        "NZDJPY",
        "USDCAD",
        "USDCHF",
        "USDJPY",
        "CADCHF",
        "CADJPY",
        "CHFJPY",
    ]

    for ticker in tickers:
        base, quote = ticker[:3], ticker[3:]

        cur_pair = make_pair(base + quote)
        assert ticker == cur_pair.ticker

        cur_pair = make_pair(quote + base)
        assert ticker == cur_pair.ticker

        pip = 0.01 if "JPY" in ticker else 0.0001
        assert pip == cur_pair.pip
