from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from ..core import Data

if TYPE_CHECKING:
    import pandas as pd


class Backtester(ABC):
    def __init__(self, data: Data):
        self.data = data

    @abstractmethod
    def run(self, *args) -> dict:
        pass
