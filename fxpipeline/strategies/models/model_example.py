from ...core import CandlesWindow, TradeIntent


class Strategy:
    def __init__(self):
        pass

    def get_intent(self, window: CandlesWindow):
        n = 3
        C = [window.candle(i) for i in range(-n, 0)]
        closes = [c.close for c in C]
        p = closes[-1]

        soldiers_up = all(c.body > 0 for c in C)
        soldiers_down = all(c.body < 0 for c in C)

        if soldiers_up:
            risk = p - closes[-n] + 0.1
            return TradeIntent(window.pair, p, p - risk, p + risk * 2)
        elif soldiers_down:
            risk = closes[-n] - p + 0.1
            return TradeIntent(window.pair, p, p + risk, p - risk * 2)
