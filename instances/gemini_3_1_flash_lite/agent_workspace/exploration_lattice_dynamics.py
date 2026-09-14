import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def coupled_map_lattice(size=50, steps=100, coupling=0.1, r=3.8):
    # Logistic map: x_{n+1} = r * x_n * (1 - x_n)
    # Coupled Map Lattice (CML)
    x = np.random.rand(size)
    history = []
    
    for _ in range(steps):
        history.append(x.copy())
        # Diffusion coupling
        x_next = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        x = x_next
        
    return np.array(history)

def calculate_complexity(data):
    # Simplified complexity metric: standard deviation of the spatial distribution
    return np.std(data, axis=1)

# Explore parameter space
couplings = [0.01, 0.1, 0.5]
rs = [3.5, 3.8, 4.0]

plt.figure(figsize=(12, 8))
for i, r in enumerate(rs):
    for j, c in enumerate(couplings):
        history = coupled_map_lattice(size=50, steps=100, coupling=c, r=r)
        complexity = calculate_complexity(history)
        plt.subplot(3, 3, i*3 + j + 1)
        plt.plot(complexity)
        plt.title(f"r={r}, c={c}")
        plt.ylim(0, 0.5)

plt.tight_layout()
plt.savefig('cml_parameter_exploration.png')
print("CML parameter exploration completed.")
