from itertools import combinations


# --- Currencies

# TODO: would be nice to remember what exotic pairs are not available

# TODO[Tickers]: hard code pairs instead, so we can reference from dict, begin by fetching list of pairs from Polygon API

MAJOR_CURRENCIES = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF"]
MINOR_CURRENCIES = ["NZD", "SEK", "NOK", "SGD", "HKD"]
EXOTIC_CURRENCIES = ["THB", "ZAR", "MXN", "TRY", "PLN", "CZK"]

G10_CURRENCIES = MAJOR_CURRENCIES + ["NZD", "SEK", "NOK"]
EMERGING_MARKET_CURRENCIES = ["THB", "ZAR", "MXN", "TRY", "PLN", "IDR", "MYR"]
ASIAN_CURRENCIES = ["JPY", "CNY", "KRW", "THB", "SGD", "MYR", "IDR", "PHP"]
EUROPEAN_CURRENCIES = ["EUR", "GBP", "CHF", "SEK", "NOK", "PLN", "CZK"]


CURRENCY_METADATA = {
    "USD": {"country": "United States", "region": "North America", "type": "major"},
    "EUR": {"country": "Eurozone", "region": "Europe", "type": "major"},
    "JPY": {"country": "Japan", "region": "Asia", "type": "major"},
    "GBP": {"country": "United Kingdom", "region": "Europe", "type": "major"},
    "AUD": {"country": "Australia", "region": "Oceania", "type": "major"},
    "CAD": {"country": "Canada", "region": "North America", "type": "major"},
    "CHF": {"country": "Switzerland", "region": "Europe", "type": "major"},
    "NZD": {"country": "New Zealand", "region": "Oceania", "type": "minor"},
    "SEK": {"country": "Sweden", "region": "Europe", "type": "minor"},
    "NOK": {"country": "Norway", "region": "Europe", "type": "minor"},
    "SGD": {"country": "Singapore", "region": "Asia", "type": "minor"},
    "THB": {"country": "Thailand", "region": "Asia", "type": "exotic"},
    "ZAR": {"country": "South Africa", "region": "Africa", "type": "exotic"},
}


def all_currencies():
    return sorted(set(MAJOR_CURRENCIES + MINOR_CURRENCIES + EXOTIC_CURRENCIES))


def by_region(region: str):
    return [c for c, meta in CURRENCY_METADATA.items() if meta["region"] == region]


def by_type(currency_type: str):
    return [c for c, meta in CURRENCY_METADATA.items() if meta["type"] == currency_type]


# --- Pairs

class CurrencyPair:
    currencies_ordering = [
        "EUR", "SEK", "NOK", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "JPY", "THB"
    ]  # TODO[Tickers]: hard code pairs instead, begin by fetching list of pairs from Polygon API
    priority = {}
    for i, cur in enumerate(currencies_ordering):
        priority[cur] = len(currencies_ordering) - i

    def __init__(self, *args, enforce_priority=True):
        if len(args) == 1:
            cur_1 = args[0][:3]
            cur_2 = args[0][3:]
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
