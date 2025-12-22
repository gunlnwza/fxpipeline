from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .price import ForexPrice


@dataclass
class Data:
    price: ForexPrice

    def __len__(self) -> int:
        return len(self.price)
