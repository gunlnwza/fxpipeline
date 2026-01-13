from dataclasses import dataclass

from .error import InvalidOrder


@dataclass
class Order:
    side: str
    open_price: float
    sl: float
    tp: float

    opened: bool = False
    closed: bool = False
    close_price: float = None
    close_reason: str = None

    def __post_init__(self):
        if self.side == "buy":
            if self.sl >= self.open_price:
                raise InvalidOrder("bad sl")
            elif self.tp <= self.open_price:
                raise InvalidOrder("bad tp")
        else:
            if self.sl <= self.open_price:
                raise InvalidOrder("bad sl")
            elif self.tp >= self.open_price:
                raise InvalidOrder("bad tp")

    def process_bar(self, o, h, l, c):
        if not self.opened:
            if self.side == "buy":
                if l <= self.open_price <= h:
                    self.opened = True
            else:
                if l <= self.open_price <= h:
                    self.opened = True

        if self.side == "buy":
            if l <= self.sl:
                self.closed = True
                self.close_reason = "sl"
            elif h >= self.tp:
                self.closed = True
                self.close_reason = "tp"
        else:
            if h >= self.sl:
                self.closed = True
                self.close_reason = "sl"
            elif l <= self.tp:
                self.closed = True
                self.close_reason = "tp"
