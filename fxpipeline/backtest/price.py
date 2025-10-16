class PricePoint:
    def __init__(self, index: int, price: float):
        self.index = index
        self.price = price

    def __repr__(self) -> str:
        return f"({self.index}, {self.price})"
