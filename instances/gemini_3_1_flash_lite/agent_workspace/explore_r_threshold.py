import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_mean_variance(r, c=0.3, size=50, steps=500):
    x = np.random.rand(size)
    # Burn-in
    for _ in range(500):
        x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
    
    variances = []
    for _ in range(steps):
        x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        variances.append(np.var(x))
    return np.mean(variances)

r_vals = np.linspace(3.0, 4.0, 50)
mean_vars = [get_mean_variance(r) for r in r_vals]

plt.figure(figsize=(10, 6))
plt.plot(r_vals, mean_vars)
plt.xlabel('Non-linearity (r)')
plt.ylabel('Mean Spatial Variance')
plt.title('Threshold Analysis: Non-linearity vs Synchronization Stability')
plt.grid(True)
plt.savefig('r_threshold.png')
