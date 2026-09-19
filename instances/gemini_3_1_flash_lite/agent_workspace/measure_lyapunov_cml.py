import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def measure_divergence(coupling=0.3, steps=100, size=100, r=3.949):
    x1 = np.random.rand(size)
    x2 = x1 + 1e-10  # Tiny perturbation
    divergence = []
    
    for _ in range(steps):
        # Update lattice 1
        x1 = (1 - coupling) * (r * x1 * (1 - x1)) + (coupling / 2) * (np.roll(r * x1 * (1 - x1), 1) + np.roll(r * x1 * (1 - x1), -1))
        # Update lattice 2
        x2 = (1 - coupling) * (r * x2 * (1 - x2)) + (coupling / 2) * (np.roll(r * x2 * (1 - x2), 1) + np.roll(r * x2 * (1 - x2), -1))
        
        diff = np.sqrt(np.mean((x1 - x2)**2))
        divergence.append(diff)
        
    return divergence

div = measure_divergence()

plt.figure(figsize=(10, 6))
plt.semilogy(div)
plt.xlabel('Time Step')
plt.ylabel('Divergence (log scale)')
plt.title('Divergence of Two Slightly Perturbed Lattices')
plt.grid(True)
plt.savefig('lattice_divergence.png')
