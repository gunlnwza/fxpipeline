import signal
import sys
import os

import gymnasium as gym
from stable_baselines3 import DQN

def sigint_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)


env = gym.make("CartPole-v1", render_mode="human")

use_existing = True
filename = "dqn_cartpole"
if use_existing and os.path.exists(f"{filename}.zip"):
    model = DQN.load(filename, env)
    model.exploration_initial_eps = 0.10
    model.exploration_final_eps = 0.05
    print("Loaded model")
else:
    model = DQN("MlpPolicy", env,
                exploration_fraction=0.5,
                exploration_initial_eps=0.20,
                exploration_final_eps=0.05,
                verbose=1)
    print("Created new model")

obs, _ = env.reset()
last_i = 0
for i in range(2000):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, _ = env.step(action)
    if i % 25 == 0:
        print(i, obs)
    if terminated:
        print(f"Terminated, Survived for {i - last_i} frame")
        break

env.close()
