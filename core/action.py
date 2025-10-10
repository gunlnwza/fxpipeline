from dataclasses import dataclass

from .data import Ticker


@dataclass
class Action:
    type: str


class BuyAction(Action):
    def __init__(self, size: float, ticker: Ticker):
        super().__init__("buy")
        self.size = size
        self.ticker = ticker


class SellAction(Action):
    def __init__(self, size: float, ticker):
        super().__init__("sell")
        self.size = size
        self.ticker = ticker


class CloseAction(Action):
    def __init__(self):
        super().__init__("close")


class HoldAction(Action):
    def __init__(self):
        super().__init__("hold")
