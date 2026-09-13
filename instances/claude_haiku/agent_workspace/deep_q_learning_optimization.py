import gym
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env

# Define the optimization problem environment
class OptimizationEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Discrete(11)
        self.observation_space = gym.spaces.Box(low=-np.pi, high=np.pi, shape=(1,))
        self.state = np.random.uniform(-np.pi, np.pi)

    def step(self, action):
        self.state = self.state + (action - 5) * 0.1
        reward = -np.sin(self.state) - np.cos(2 * self.state)
        done = False
        return [self.state], reward, done, {}

    def reset(self):
        self.state = np.random.uniform(-np.pi, np.pi)
        return [self.state]

# Create the optimization environment and check its validity
env = OptimizationEnv()
check_env(env)

# Train a DQN agent to solve the optimization problem
model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)

# Evaluate the trained agent
obs = env.reset()
while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, done, info = env.step(action)
    print(f"Objective value: {-rewards}")
    if done:
        break