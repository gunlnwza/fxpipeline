from ..core import Data, PriceRequest


class Loader:
    def __init__(self):
        pass

    def load(self, req: PriceRequest) -> Data:
        raise NotImplementedError
