import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_stable_attractor_density(r_range, c_range, size=50, transient=1000, measure_steps=200):
    density = np.zeros((len(r_range), len(c_range)))
    for i, r in enumerate(r_range):
        for j, c in enumerate(c_range):
            # Average over 5 random initial conditions
            spreads = []
            for _ in range(5):
                x = np.random.rand(size)
                for _ in range(transient):
                    x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
                
                # Measure after settling
                spreads.append(np.std(x))
            density[i, j] = np.mean(spreads)
    return density

r_vals = np.linspace(3.7, 4.0, 50)
c_vals = np.linspace(0.0, 0.5, 50)
data = get_stable_attractor_density(r_vals, c_vals)

plt.figure(figsize=(10, 8))
plt.imshow(data, extent=[c_vals.min(), c_vals.max(), r_vals.min(), r_vals.max()], origin='lower', aspect='auto', cmap='magma')
plt.colorbar(label='Avg Attractor Spread (Std Dev)')
plt.xlabel('Coupling Strength')
plt.ylabel('Logistic Parameter r')
plt.title('Stability Analysis: Attractor Landscape')
plt.savefig('stability_bifurcation.png')
