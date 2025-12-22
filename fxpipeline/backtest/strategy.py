from .bt_core import PriceWindow, TradeIntent

# TODO: make enum
OPEN = 0
HIGH = 1
LOW = 2
CLOSE = 3

class Strategy:
    def __init__(self):
        pass

    def get_intent(self, window: PriceWindow):
        cur = window[-1]
        prev = window[-2]

        if cur[CLOSE] > prev[CLOSE]:
            risk = cur[CLOSE] - cur[LOW]
            stop_loss = cur[CLOSE] - risk
            take_profit = cur[CLOSE] + risk * 2
            return TradeIntent(window.pair, cur[CLOSE], stop_loss, take_profit)
