from fxpipeline.backtest import TradingEnv
from fxpipeline.ingestion import load_forex_price
from fxpipeline.utils import handle_sigint
from fxpipeline.strategy import Model


# TODO: This has to go, make wrappers instead
def get_action(model, obs):
    obs = obs.reshape((1, -1))
    action = model.predict(obs)
    action = action[0]

    threshold = 1  # z-score
    if action > threshold:
        action = 1
    elif action < -threshold:
        action = -1
    else:
        action = 0
    return action


def main():
    handle_sigint()

    df = load_forex_price("EURUSD")
    env = TradingEnv(df, obs_size=50, render_mode="human")
    model = Model()

    obs, info = env.reset()
    while True:
        action = get_action(model, obs)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    env.close()


if __name__ == "__main__":
    main()
