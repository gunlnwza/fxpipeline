from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..backtest import Account, PricePoint


class Strategy(ABC):
    @abstractmethod
    def act(self, account: Account, point: PricePoint):  # TODO[architecure]: make act() signature good
        pass
