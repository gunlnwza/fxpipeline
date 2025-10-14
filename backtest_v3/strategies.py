import random

from .core import State, Action, BuyAction, SellAction, CloseAction, HoldAction


# TODO: REFACTOR REFACTOR REFACTOR REFACTOR REFACTOR
# TODO: refactor the crossover logic
# TODO: it's just so hard to access state's attributes: account, data


class Strategy:
    def __init__(self):
        self._history = None  # thought processes, logs, etc.

    def think(self, state: State) -> list[Action]:
        pass


class BuyAndHold(Strategy):
    def __init__(self, *, choice="buy"):
        super().__init__()
        self._buy = False
        self._choice = choice

    def think(self, state: State) -> list[Action]:
        actions = []
        if not self._buy:
            size = state.account.balance * 0.0001
            ticker = state.data.metadata.ticker
            if self._choice == "buy":
                actions.append(BuyAction(size, ticker))
            else:
                actions.append(SellAction(size, ticker))
            self._buy = True
        return actions


class AccountBlower(BuyAndHold):
    def __init__(self, size):
        super().__init__()
        self.size = size

    def think(self, state: State) -> list[Action]:
        if not self._buy:
            self._buy = True
            ticker = state.data.metadata.ticker
            return [BuyAction(self.size, ticker)]
        return []


class SellAndHold(BuyAndHold):
    def __init__(self):
        super().__init__(choice="sell")


class RandomAction(Strategy):
    def __init__(self, *, buy_weight=1, sell_weight=1,
                 close_weight=1, hold_weight=1, seed=None):
        super().__init__()
        self._weights = (buy_weight, sell_weight, close_weight, hold_weight)
        self._rng = random.Random(seed)

    def think(self, state: State) -> list[Action]:
        choice = self._rng.choices(
            ("buy", "sell", "close", "hold"),
            weights=self._weights
        )[0]
        have_order = state.account.order
        if choice in ("buy", "sell") and have_order:
            choice = "hold"

        size = state.account.balance * 0.00001
        ticker = state.data.metadata.ticker
        match choice:
            case "buy": action = BuyAction(size, ticker)
            case "sell": action = SellAction(size, ticker)
            case "close": action = CloseAction()
            case "hold": action = HoldAction()
        return [action]


class MACrossover(Strategy):
    def __init__(self):
        super().__init__()

    def think(self, state: State) -> list[Action]:
        actions = []

        df = state.data.df
        i = state.row_index

        # index-0 is now, index-1 is prev
        fast = (df["fast_ma"].iloc[i], df["fast_ma"].iloc[i - 1])
        slow = (df["slow_ma"].iloc[i], df["slow_ma"].iloc[i - 1])
        cross_up = fast[1] < slow[1] and fast[0] > slow[0]
        cross_down = fast[1] > slow[1] and fast[0] < slow[0]

        order = state.account.order
        type = order.type if order else None
        size = state.account.equity * 0.00001
        ticker = state.data.metadata.ticker
        if cross_up:
            if type == "sell":
                actions.append(CloseAction())
            actions.append(BuyAction(size, ticker))
        elif cross_down:
            if type == "buy":
                actions.append(CloseAction())
            actions.append(SellAction(size, ticker))

        return actions


class RSIZone(Strategy):
    def __init__(self):
        super().__init__()

    def think(self, state: State) -> list[Action]:
        df = state.data.df
        i = state.row_index

        rsi = df["rsi"].iloc[i]

        order = state.account.order
        type = order.type if order else None
        size = state.account.equity * 0.00001

        if type == "buy":
            if rsi > 50:
                return [CloseAction()]
        elif type == "sell":
            if rsi < 50:
                return [CloseAction()]

        actions = []
        if rsi < 30:
            if order and type == "buy":
                pass
            else:
                if order:
                    actions.append(CloseAction())
                actions.append(BuyAction(size, state.data.metadata.ticker))
        elif rsi > 70:
            if order and type == "sell":
                pass
            else:
                if order:
                    actions.append(CloseAction())
                actions.append(SellAction(size, state.data.metadata.ticker))

        return actions


class MACDCrossover(Strategy):
    def __init__(self):
        super().__init__()

    def think(self, state: State) -> list[Action]:
        actions = []

        df = state.data.df
        i = state.row_index

        # index-0 is now, index-1 is prev
        macd = (df["macd"].iloc[i], df["macd"].iloc[i - 1])
        signal = (df["macd_signal"].iloc[i], df["macd_signal"].iloc[i - 1])
        cross_up = macd[1] < signal[1] and macd[0] > signal[0]
        cross_down = macd[1] > signal[1] and macd[0] < signal[0]

        order = state.account.order
        type = order.type if order else None
        size = state.account.equity * 0.00001
        if cross_up:
            if order and type == "buy":
                pass
            else:
                if order:
                    actions.append(CloseAction())
                actions.append(BuyAction(size, state.data.metadata.ticker))
        elif cross_down:
            if order and type == "sell":
                pass
            else:
                if order:
                    actions.append(CloseAction())
                actions.append(SellAction(size, state.data.metadata.ticker))

        return actions



class MAAndRSI(Strategy):
    def __init__(self):
        super().__init__()

    def think(self, state: State) -> list[Action]:
        actions = []

        df = state.data.df
        i = state.row_index

        # index-0 is now, index-1 is prev
        macd = (df["macd"].iloc[i], df["macd"].iloc[i - 1])
        signal = (df["macd_signal"].iloc[i], df["macd_signal"].iloc[i - 1])
        fast_ma = (df["fast_ma"].iloc[i],)
        slow_ma = (df["slow_ma"].iloc[i],)
        rsi = (df["rsi"].iloc[i],)
        price = (df["close"].iloc[i], )

        buy_zone = rsi[0] > 60 and fast_ma[0] > slow_ma[0]
        sell_zone = rsi[0] < 40 and fast_ma[0] < slow_ma[0]

        order = state.account.order
        type = order.type if order else None
        size = state.account.equity * 0.00001
        
        if buy_zone:
            if order and type == "buy":
                pass
            else:
                if order:
                    actions.append(CloseAction())
                actions.append(BuyAction(size, state.data.metadata.ticker))
        elif sell_zone:
            if order and type == "sell":
                pass
            else:
                if order:
                    actions.append(CloseAction())
                actions.append(SellAction(size, state.data.metadata.ticker))
        else:
            if order:
                actions.append(CloseAction())

        return actions
    