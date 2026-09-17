import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def simulate_lattice_evolution(size=100, steps=200, coupling=0.5, r=3.949):
    x = np.random.rand(size)
    lattice_history = np.zeros((steps, size))
    for t in range(steps):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        lattice_history[t, :] = x
    return lattice_history

history = simulate_lattice_evolution()

plt.figure(figsize=(10, 8))
plt.imshow(history, aspect='auto', cmap='viridis', interpolation='nearest')
plt.colorbar(label='State value')
plt.xlabel('Lattice Node Index')
plt.ylabel('Time Step')
plt.title('Space-Time Evolution of CML (r=3.949, coupling=0.5)')
plt.savefig('lattice_spatiotemporal_evolution.png')
