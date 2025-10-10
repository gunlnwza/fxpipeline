from dataclasses import dataclass
import datetime as dt


@dataclass
class PricePoint:
    index: int  # row number
    time: dt.datetime  # timestamp

    price: float  # close price

    def to_tuple(self) -> tuple:
        return (self.index, self.time, self.price)
