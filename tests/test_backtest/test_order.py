from fxpipeline.backtest.data import Order

buy = Order("buy", 0, 21)
sell = Order("sell", 0, 21)


def test_init():
    assert buy._open_i == 0
    assert buy._open_price == 21
    assert buy._close_i is None
    assert buy._close_price is None


def test_current_profit():
    assert buy.current_profit(42) == 21
    assert sell.current_profit(42) == -21


def test_close():
    buy.close(1, 42)
    assert buy._close_i == 1
    assert buy._close_price == 42


def test_get_info():
    info = buy.get_info()
    assert set(info.keys()) == {"type", "close_i", "close_price", "open_i", "open_price"}
    assert info["type"] == "buy"
    assert info["open_i"] == 0
    assert info["open_price"] == 21
    assert info["close_i"] == 1
    assert info["close_price"] == 42
