from dataclasses import dataclass

from .data import PriceMetaData


@dataclass
class DataRequest:
    pass


@dataclass
class PriceRequest(DataRequest, PriceMetaData):
    pass
