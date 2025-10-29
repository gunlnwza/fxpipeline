from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class TradingEnv:
    def __init__(self, price_series: pd.Series, window=100, initial_balance=1000):
        self.price = price_series
        self.window = window
        self.balance = initial_balance
        self.position = 0  # -1 = short, 0 = flat, 1 = long
        self.current_step = window
        self.history = []

    def get_observation(self):
        window_data = self.price[self.current_step - self.window: self.current_step]
        zscore = (window_data - window_data.mean()) / window_data.std()
        return zscore.to_numpy()

    def step(self, action: int):
        # action: 0 = short, 1 = flat, 2 = long
        price_now = self.price.iloc[self.current_step]
        price_next = self.price.iloc[self.current_step + 1]

        # Calculate PnL
        pnl = 0
        if action == 0:
            pnl = self.position * (price_now - price_next)
            self.position = -1
        elif action == 2:
            pnl = self.position * (price_next - price_now)
            self.position = 1
        else:
            pnl = 0
            self.position = 0

        self.balance += pnl
        self.history.append((self.current_step, action, pnl, self.balance))

        self.current_step += 1
        done = self.current_step + 1 >= len(self.price)

        return self.get_observation(), pnl, done, {}

    def reset(self):
        self.current_step = self.window
        self.balance = 1000
        self.position = 0
        self.history = []
        return self.get_observation()
