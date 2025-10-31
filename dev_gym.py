import gymnasium as gym

class MyEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.action_space = None
        self.observation_space = None
        self.spec = None
        self.metadata = None
        self.np_random = None
    
    def step(self):
        """Update environment with actions"""
        pass

    def reset(self):
        """Reset environment to initial state"""
        pass

    def render():
        """Visualize what the agent see"""
        pass

    def close():
        """Close environemnt, free stuffs"""
        pass

# TradingEnv will be used when vectorized pandas cannot simulate the details anymore
env = MyEnv()
