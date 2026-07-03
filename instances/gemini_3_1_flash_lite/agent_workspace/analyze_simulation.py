import numpy as np
import matplotlib.pyplot as plt

# Load saved simulation states
states = np.load('simulation_states.npy')

# Calculate the density of active cells per step to measure complexity/stability
densities = [np.sum(state) / state.size for state in states]

# Plot the density trend
plt.figure(figsize=(10, 5))
plt.plot(densities, marker='o', linestyle='-')
plt.title('Evolution of System Density (Complexity Metric)')
plt.xlabel('Step')
plt.ylabel('Density of Active Cells')
plt.savefig('density_trend.png')
print("Analysis complete. Density plot saved.")
