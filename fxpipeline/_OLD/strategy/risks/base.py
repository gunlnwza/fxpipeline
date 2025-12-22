from abc import ABC, abstractmethod


class RiskController(ABC):
    """Control orders sending behavior, lot size, stoploss, take-profit, ..."""

    @abstractmethod
    def act(self, account: Account, point: PricePoint, signal: bool):
        """Decide how to act on data given current `point` and `signal`"""
