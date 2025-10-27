from itertools import combinations


class CurrencyPair:
    currencies_ordering = [
        "EUR", "SEK", "NOK", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "JPY", "THB"
    ]  # TODO[Tickers]: hard code pairs instead, begin by fetching list of pairs from Polygon API
    priority = {}
    for i, cur in enumerate(currencies_ordering):
        priority[cur] = len(currencies_ordering) - i

    def __init__(self, *args: str | list[str], enforce_priority=True):
        if len(args) == 1:
            cur_1, cur_2 = args[0][:3], args[0][3:]
        elif len(args) == 2:
            cur_1, cur_2 = args
        else:
            raise ValueError("Invalid arguments format")

        cur_1 = cur_1.upper()
        cur_2 = cur_2.upper()

        # swap currencies if the 1st is less than 2nd in prestiege (we need 1st > 2nd)
        if enforce_priority:
            importance_1 = CurrencyPair.priority.get(cur_1, -1)
            importance_2 = CurrencyPair.priority.get(cur_2, -1)
            if importance_1 < importance_2:
                cur_1, cur_2 = cur_2, cur_1

        self.base = cur_1
        self.quote = cur_2

    @property
    def ticker(self):
        return self.base + self.quote

    def reverse(self):
        return CurrencyPair(self.quote, self.base, enforce_priority=False)

    def __repr__(self):
        return f"CurrencyPair({self.base}, {self.quote})"

    def __str__(self):
        return self.ticker    


def make_pairs(currencies: list[str]) -> list[CurrencyPair]:
    return [CurrencyPair(cur_1, cur_2) for cur_1, cur_2 in combinations(currencies, 2)]
