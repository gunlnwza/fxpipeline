from dataclasses import dataclass

from .loader.loader import Data
from .core import Account, State, Action
from ..to_write.strategies import Strategy
from ..untrack.metrics import Summary
from ..utils.utils import PrettyLogger


@dataclass
class SimulationConfig:
    data: Data
    account: Account
    strategy: Strategy


log = PrettyLogger("forex")


def do_actions(state: State, actions: list[Action]):
    """actions: action queue, do from left to right, in that order"""
    if not actions:
        return
    account = state.account
    cur = state.current_point
    for action in actions:
        match action.type:
            case "buy": account.buy(cur, action)
            case "sell": account.sell(cur, action)
            case "close": account.close(cur)
            case "hold": pass
            case _: raise ValueError(f"invalid action '{type}'")


def simulate(config: SimulationConfig):
    state = State(config.data, config.account)
    strategy = config.strategy

    n = len(state.data.df)
    for _ in range(n):
        actions = strategy.think(state)
        do_actions(state, actions)
        state.account.update(state.current_point)
        if state.account.equity <= 0:
            log.error("Account blown")
            break
        state.reveal_next_bar()

    state.account.close(state.current_point)
    return Summary(state.data, state.account, strategy)
