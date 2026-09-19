import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_stable_attractor_density(r_range, c_range, size=30, transient=500):
    density = np.zeros((len(r_range), len(c_range)))
    for i, r in enumerate(r_range):
        for j, c in enumerate(c_range):
            x = np.random.rand(size)
            for _ in range(transient):
                x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
            density[i, j] = np.std(x)
    return density

r_vals = np.linspace(3.7, 4.0, 30)
c_vals = np.linspace(0.0, 0.5, 30)
data = get_stable_attractor_density(r_vals, c_vals)

plt.figure(figsize=(8, 6))
plt.imshow(data, extent=[c_vals.min(), c_vals.max(), r_vals.min(), r_vals.max()], origin='lower', aspect='auto', cmap='magma')
plt.colorbar(label='Attractor Spread')
plt.xlabel('Coupling Strength')
plt.ylabel('Logistic Parameter r')
plt.title('Stability Analysis: Attractor Landscape')
plt.savefig('stability_bifurcation.png')
