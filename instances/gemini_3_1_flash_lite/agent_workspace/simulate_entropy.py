import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Simulation of a simple system evolving towards structure from entropy
def generate_state(n=1000):
    # Start with random noise
    state = np.random.rand(n, 2)
    # Apply a simple rule to encourage local clustering
    for _ in range(50):
        # Move closer to the average of neighbors
        for i in range(n):
            dist = np.sqrt(np.sum((state - state[i])**2, axis=1))
            neighbors = state[dist < 0.1]
            if len(neighbors) > 1:
                center = np.mean(neighbors, axis=0)
                state[i] += (center - state[i]) * 0.1
    return state

state = generate_state()
plt.figure(figsize=(6, 6))
plt.scatter(state[:, 0], state[:, 1], s=1, alpha=0.5)
plt.title('Emergence from Entropy')
plt.axis('off')
plt.savefig('emergence.png')
