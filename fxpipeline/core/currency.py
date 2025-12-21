from dataclasses import dataclass

CURRENCY_RANK = [
    "EUR",
    "GBP",
    "AUD",
    "NZD",
    "USD",
    "CAD",
    "CHF",
    "JPY",
    "SEK",
    "NOK",
    "SGD",
    "HKD",
    "THB",
    "ZAR",
]


@dataclass
class CurrencyPair:
    base: str
    quote: str
    pip: float

    @property
    def ticker(self):
        return self.base + self.quote

    def copy(self):
        return CurrencyPair(self.base, self.quote, self.pip)

    def reverse(self):
        self.base, self.quote = self.quote, self.base

    def __repr__(self):
        return f"CurrencyPair({self.base}, {self.quote}, {self.pip})"

    def __str__(self):
        return self.ticker


def _sort_base_quote(base: str, quote: str) -> tuple[str, str]:
    inf = float("inf")

    rank_base = inf
    rank_quote = inf
    for i, currency in enumerate(CURRENCY_RANK):
        if rank_base < inf and rank_quote < inf:
            break
        if base == currency:
            rank_base = i
        elif quote == currency:
            rank_quote = i

    if rank_base > rank_quote:
        base, quote = quote, base
    return base, quote


def _get_pip(base: str, quote: str) -> float:
    if base == "JPY" or quote == "JPY":
        return 0.01
    return 0.0001


def make_pair(ticker: str | CurrencyPair) -> CurrencyPair:
    if isinstance(ticker, CurrencyPair):
        return ticker.copy()

    if len(ticker) != 6:
        raise ValueError(f"Invalid ticker string '{ticker}'")

    base, quote = ticker[:3], ticker[3:]
    base, quote = _sort_base_quote(base, quote)
    pip = _get_pip(base, quote)
    return CurrencyPair(base, quote, pip)
