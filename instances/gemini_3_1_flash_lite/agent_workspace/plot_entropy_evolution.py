import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def calculate_shannon_entropy(lattice, bins=10):
    hist, _ = np.histogram(lattice, bins=bins)
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log2(p))

def simulate_entropy_over_time(r, size=100, steps=200, coupling=0.1):
    x = np.random.rand(size)
    entropy_history = []
    for _ in range(steps):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        entropy_history.append(calculate_shannon_entropy(x))
    return entropy_history

e1 = simulate_entropy_over_time(r=3.5)
e2 = simulate_entropy_over_time(r=3.949)

plt.figure(figsize=(10, 5))
plt.plot(e1, label='Below Ceiling (r=3.5)')
plt.plot(e2, label='Above Ceiling (r=3.949)')
plt.xlabel('Time Step')
plt.ylabel('Spatial Shannon Entropy')
plt.title('Entropy Evolution in CML')
plt.legend()
plt.savefig('entropy_evolution.png')
