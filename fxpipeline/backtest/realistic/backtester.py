from ...strategy.risks.risk_control import RiskController
from .account import Account

from ..base import Backtester, PricePoint
from ...strategy.signals.signal_gen import SignalGenerator


class RealisticBacktester(Backtester):
    def __init__(self, data, acc=None):
        super().__init__(data)
        self.acc = acc if acc else Account()

    def run(self, signal: SignalGenerator, risk: RiskController):
        account = Account()
        signals = signal.generate_batch(self.data)
        for i, row in enumerate(self.data.ohlc_df.iterrows()):
            timestamp, ohlc = row
            point = PricePoint(timestamp, ohlc["close"])
            signal = signals[i]

            risk.act(account, point, signal)
            account.update(point)
            if account.is_blown():
                break

        account.summarize(point)
        return dict(account)
