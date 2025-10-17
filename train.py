import os

import gymnasium as gym
from stable_baselines3 import DQN

import gymnasium as gym

class StayCenteredReward(gym.RewardWrapper):
    def reward(self, reward):
        cart_pos = self.unwrapped.state[0]
        cart_vel = self.unwrapped.state[1]
        pole_angle = self.unwrapped.state[2]
        pole_angular_vel = self.unwrapped.state[3]

        reward -= abs(cart_pos) * 1  # don't stay away from center
        reward -= abs(pole_angular_vel) * 1  # don't jerk pole around
        if cart_pos < 0:  # at left side
            reward += pole_angle * 2  # tilt pole right
        else:  # at right side
            reward -= pole_angle * 2  # tilt pole left

        return reward 

env = gym.make("CartPole-v1")
env = StayCenteredReward(env)

filename = "dqn_cartpole"
if os.path.exists(f"{filename}.zip"):
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

model.learn(total_timesteps=30_000)
model.save(filename)
