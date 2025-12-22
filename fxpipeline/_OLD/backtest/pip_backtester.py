import pandas as pd

from ..strategy.signals.signal_gen import SignalGenerator

from .base import Backtester


class PipsBacktester(Backtester):
    def __init__(self, data):
        super().__init__(data)

    def run(self, signal_gen: SignalGenerator):
        signals = signal_gen.generate_batch(
            self.data
        )  # will already be left-padded if it need warmup
        price = self.data.price
        df = price.df.copy()

        df["buying"] = signals
        df["prev_close"] = df["close"].shift(1)
        df["pips"] = (df["close"] - df["prev_close"]) / price.pair.pip

        total_pips = round((df["pips"] * df["buying"]).sum())
        return {"total_pips": total_pips}
