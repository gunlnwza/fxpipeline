from typing import TYPE_CHECKING
import os
import argparse

import matplotlib.pyplot as plt
from stable_baselines3 import DQN

if TYPE_CHECKING:
    from .trading_env import TradingEnv
else:
    from trading_env import TradingEnv


def get_model(name, env):
    if os.path.exists(f"{name}.zip"):
        print("Load model")
        return DQN.load(name, env)
    else:
        print("Create new model")
        return DQN("MlpPolicy", env, verbose=1)


def train(model, timesteps):
    model.learn(timesteps)
    model.save("baseline")


def plot_result(prices, fast_ma, slow_ma, buys):
    plt.figure(figsize=(12, 6))
    plt.title("Result")
    plt.xlabel("Index")
    plt.ylabel("Price")
    
    plt.plot(prices)
    plt.plot(fast_ma)
    plt.plot(slow_ma)
    for band in buys:
        plt.axvspan(band[0], band[1], color="green", alpha=0.3)

    plt.show()

def test(model, env):
    buys: list[tuple[int]] = []
    opened_order_index = None

    obs, info = env.reset()
    for i in range(1000):
        action, _ = model.predict(obs)
        if opened_order_index:
            if action == 0:
                buys.append((opened_order_index, i))
                opened_order_index = None
        else:
            if action == 1:
                opened_order_index = i
    
        obs, reward, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            break

    plot_result(env.prices, env.fast_ma, env.slow_ma, buys)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="EURUSD")
    parser.add_argument("--timesteps", type=int, default=10000)
    parser.add_argument("-t", "--test", action="store_false")
    args = parser.parse_args()

    env = TradingEnv(f".polygon_cache/{args.ticker}", 42)
    model = get_model("baseline", env)
    if args.test:
        print("Train")
        train(model, args.timesteps)
    else:
        print("Test")
        test(model, env)


if __name__ == "__main__":
    main()
