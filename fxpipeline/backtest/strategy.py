from ..core import CandlesWindow, TradeIntent


class Strategy:
    def __init__(self):
        pass

    def get_intent(self, window: CandlesWindow):
        cur = window.candle(-1)
        prev = window.candle(-2)

        if cur.close > prev.close:
            risk = (cur.close - cur.low)
            return TradeIntent(
                window.pair,
                cur.close,
                cur.close - risk,
                cur.close + risk * 2
            )
