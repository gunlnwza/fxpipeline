from dataclasses import dataclass

from ..to_write.data import PriceMetaData


@dataclass
class DataRequest:
    pass


@dataclass
class PriceRequest(DataRequest, PriceMetaData):
    pass
