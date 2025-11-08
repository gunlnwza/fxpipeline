from abc import ABC


class Strategy(ABC):
    def act(self, obs): ...
    def reset(self): ...
    def observe(self, reward, next_obs, done, info): ...
    def train(self): ...  # for RL or learnable strategies
    def save(self, path): ...
    def load(self, path): ...


# fxpipeline/strategy/mean_revert.py
# from .base import Strategy

class MeanReversionStrategy(Strategy):
    def act(self, observation):
        z = observation[0][-1]  # Assume last obs is z-score
        if z > 1.0:
            return -1  # short
        elif z < -1.0:
            return 1   # long
        return 0  # hold


# fxpipeline/strategy/ppo_wrapper.py

class PPOAgentStrategy(Strategy):
    def __init__(self, model):
        self.model = model

    def act(self, observation):
        action, _ = self.model.predict(observation, deterministic=True)
        return int(action)


# obs = env.reset()
# done = False
# strategy = MyStrategy()

# while not done:
#     action = strategy.act(obs)
#     obs, reward, done, info = env.step(action)

def test_mean_reversion_logic():
    strat = MeanReversionStrategy()
    obs = [[0.0, 0.5, 1.2]]  # z-score = 1.2 → short
    assert strat.act(obs) == -1
