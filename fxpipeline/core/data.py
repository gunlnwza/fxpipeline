from dataclasses import dataclass

from .price import ForexPrices


@dataclass
class Data:
    price: ForexPrices

    def __len__(self) -> int:
        return len(self.price)
