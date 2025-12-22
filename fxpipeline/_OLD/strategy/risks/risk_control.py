from ...backtest.realistic.account import Account

from ...backtest.base import PricePoint


class FixedLotSize(RiskController):
    def __init__(self, size=0.01):
        self.size = size

    def act(self, account, point, signal):
        if not signal:
            return
        account.buy(point, self.size)


# class FixedFractionRisk(RiskModule):
# def size(self, equity): ...


# class MaxOrdersRisk(RiskModule):
# def allow_open(self, current_orders): ...
