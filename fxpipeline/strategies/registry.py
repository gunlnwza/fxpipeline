from .base import Strategy

from .random_trade import RandomTradeStrategy


def register(cls):
    STRATEGIES[cls.name] = cls
    return cls


STRATEGIES = {}
register(RandomTradeStrategy)


def create_strategy(name: str) -> Strategy:
    try:
        return STRATEGIES[name]()
    except KeyError:
        raise ValueError(
            f"Unknown strategy '{name}'. "
            f"Available: {', '.join(STRATEGIES)}"
        )
