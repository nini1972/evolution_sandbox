import numpy as np
import gym
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy

# Define the environment
env = gym.make('CartPole-v1')

# Define the objective function
def objective_function(params):
    env.env.theta_threshold_radians = params[0]
    env.env.x_threshold = params[1]
    mean_reward, _ = evaluate_policy(model, env, n_eval_episodes=100)
    return -mean_reward

# Train the reinforcement learning model
model = PPO('MlpPolicy', env, verbose=0)
model.learn(total_timesteps=100000)

# Optimize the environment parameters
initial_params = [env.env.theta_threshold_radians, env.env.x_threshold]
optimal_params = fmin(objective_function, initial_params, disp=False)

# Evaluate the optimized environment
env.env.theta_threshold_radians = optimal_params[0]
env.env.x_threshold = optimal_params[1]
mean_reward, _ = evaluate_policy(model, env, n_eval_episodes=100)

print(f"Optimal environment parameters: theta_threshold={optimal_params[0]:.3f}, x_threshold={optimal_params[1]:.3f}")
print(f"Mean reward: {mean_reward:.3f}")