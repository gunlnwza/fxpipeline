from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .price import ForexPrices


@dataclass
class Data:
    price: ForexPrices

    def __len__(self) -> int:
        return len(self.price)
