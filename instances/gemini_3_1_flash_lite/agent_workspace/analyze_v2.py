import numpy as np
import matplotlib.pyplot as plt

# Load multi-state simulation
states = np.load("simulation_states_v2.npy")

# Analyze diversity of states over time
# We'll calculate the entropy (distribution of cell states)
def calculate_entropy(state):
    counts = np.bincount(state.flatten(), minlength=3)
    probs = counts / counts.sum()
    entropy = -sum(p * np.log2(p + 1e-9) for p in probs)
    return entropy

entropies = [calculate_entropy(state) for state in states]

plt.figure(figsize=(10, 5))
plt.plot(entropies, color='purple', marker='.', linestyle='-')
plt.title("System Entropy over 50 Iterations (Multi-State CA)")
plt.xlabel("Step")
plt.ylabel("Shannon Entropy")
plt.savefig("entropy_plot.png")
print("Analysis complete. Entropy plot generated.")
