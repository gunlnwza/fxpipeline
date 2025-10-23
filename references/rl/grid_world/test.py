import os
import signal
import sys

from stable_baselines3 import DQN
from train import GridWorldEnv

def handle_sigint(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)


filename = "gridworld_model"
if not os.path.exists(f"{filename}.zip"):
    sys.exit(1)

env = GridWorldEnv("human")
model = DQN.load(filename, env)

obs, _ = env.reset()
for i in range(100):
    action, _states = model.predict(obs)
    obs, reward, terminated, truncated, _ = env.step(action.item())
    if terminated or truncated:
        env.reset()

env.close()
