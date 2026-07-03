import numpy as np
import matplotlib.pyplot as plt

# Load the states
states = np.load("simulation_states.npy")

# Plotting the last state
plt.figure(figsize=(6, 6))
plt.imshow(states[-1], cmap='binary')
plt.title("Final State of Emergent Complexity")
plt.savefig("final_state.png")
print("Visual representation saved.")
