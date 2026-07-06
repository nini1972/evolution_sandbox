import numpy as np
import matplotlib.pyplot as plt

data = np.load('experiments/emergent_behavior_v3/simulation_data.npy')
densities = [np.mean(step) for step in data]

plt.figure(figsize=(10, 5))
plt.plot(densities, color='darkorange')
plt.title("System Density in Adaptive CA (V3 Experiment)")
plt.xlabel("Iteration")
plt.ylabel("Global Density")
plt.savefig('experiments/emergent_behavior_v3/density_evolution.png')
print("Analysis for V3 complete.")
