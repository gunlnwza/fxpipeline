from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .price import ForexPrice


# TODO: think about access mechanism for when data is of different length, (use timestamp)
@dataclass
class Data:
    price: ForexPrice
    economics: Optional[pd.DataFrame]

    def __len__(self) -> int:
        return len(self.price)
