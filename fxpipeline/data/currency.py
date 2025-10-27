# TODO[data]: would be nice to remember what exotic pairs are not available

# TODO[data]: hard code pairs instead, so we can reference from dict, begin by fetching list of pairs from Polygon API

# TODO[refactor]: This is smelly, make it a json file instead?
# CURRENCY_METADATA = {
#     "USD": {"country": "United States", "region": "North America", "type": "major"},
#     "EUR": {"country": "Eurozone", "region": "Europe", "type": "major"},
#     "JPY": {"country": "Japan", "region": "Asia", "type": "major"},
#     "GBP": {"country": "United Kingdom", "region": "Europe", "type": "major"},
#     "AUD": {"country": "Australia", "region": "Oceania", "type": "major"},
#     "CAD": {"country": "Canada", "region": "North America", "type": "major"},
#     "CHF": {"country": "Switzerland", "region": "Europe", "type": "major"},
#     "NZD": {"country": "New Zealand", "region": "Oceania", "type": "minor"},
#     "SEK": {"country": "Sweden", "region": "Europe", "type": "minor"},
#     "NOK": {"country": "Norway", "region": "Europe", "type": "minor"},
#     "SGD": {"country": "Singapore", "region": "Asia", "type": "minor"},
#     "THB": {"country": "Thailand", "region": "Asia", "type": "exotic"},
#     "ZAR": {"country": "South Africa", "region": "Africa", "type": "exotic"},
# }

# def all_currencies():
#     return sorted(set(MAJOR_CURRENCIES + MINOR_CURRENCIES + EXOTIC_CURRENCIES))

# def by_region(region: str):
#     return [c for c, meta in CURRENCY_METADATA.items() if meta["region"] == region]

# def by_type(currency_type: str):
#     return [c for c, meta in CURRENCY_METADATA.items() if meta["type"] == currency_type]


# TODO[data]: make currency info airtight
MAJOR_CURRENCIES = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF"]
MINOR_CURRENCIES = ["NZD", "SEK", "NOK", "SGD", "HKD"]
EXOTIC_CURRENCIES = ["THB", "ZAR", "MXN", "TRY", "PLN", "CZK"]
G10_CURRENCIES = MAJOR_CURRENCIES + ["NZD", "SEK", "NOK"]
EMERGING_MARKET_CURRENCIES = ["THB", "ZAR", "MXN", "TRY", "PLN", "IDR", "MYR"]
ASIAN_CURRENCIES = ["JPY", "CNY", "KRW", "THB", "SGD", "MYR", "IDR", "PHP"]
EUROPEAN_CURRENCIES = ["EUR", "GBP", "CHF", "SEK", "NOK", "PLN", "CZK"]


def get_currencies_by_group(name: str):
    """
    name = major, minor, exotic, g10, emerging_market, asian, european
    """
    match name:
        case "major": return MAJOR_CURRENCIES
        case "minor": return MINOR_CURRENCIES
        case "exotic": return EXOTIC_CURRENCIES
        case "g10": return G10_CURRENCIES
        case "emerging_market": return EMERGING_MARKET_CURRENCIES
        case "asian": return ASIAN_CURRENCIES
        case "european": return EUROPEAN_CURRENCIES
