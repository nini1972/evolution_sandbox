import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_attractor_density(r_range, c_range, size=50, steps=200):
    density = np.zeros((len(r_range), len(c_range)))
    for i, r in enumerate(r_range):
        for j, c in enumerate(c_range):
            x = np.random.rand(size)
            # Transient burn-in
            for _ in range(200):
                x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
            # Measure attractor spread
            density[i, j] = np.std(x)
    return density

r_vals = np.linspace(3.5, 4.0, 50)
c_vals = np.linspace(0.0, 0.5, 50)
data = get_attractor_density(r_vals, c_vals)

plt.figure(figsize=(10, 8))
plt.imshow(data, extent=[c_vals.min(), c_vals.max(), r_vals.min(), r_vals.max()], origin='lower', aspect='auto', cmap='viridis')
plt.colorbar(label='Attractor Spread (Std Dev)')
plt.xlabel('Coupling Strength')
plt.ylabel('Logistic Parameter r')
plt.title('Attractor Landscape: r vs Coupling')
plt.savefig('bifurcation_landscape.png')
