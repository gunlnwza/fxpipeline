import pandas as pd

from .data import Data
from .account import Account
from .price_point import PricePoint


class StateView:
    pass


# TODO: raise error if client tries to access future
class State:
    def __init__(self, data: Data, account: Account):
        self.data = data
        self.account = account
        self.row_index = 0

        # self.view = StateView()

    def reveal_next_bar(self):
        if self.row_index + 1 >= len(self.data.df):
            return
        self.row_index += 1

    @property
    def current_point(self) -> PricePoint:
        i = self.row_index
        time = self.data.df.index[i]
        price = self.data.df.iloc[i]["close"]
        return PricePoint(i, pd.to_datetime(time), price)
