import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def calculate_spatial_variance(coupling, steps=100, size=100, r=3.949):
    x = np.random.rand(size)
    variances = []
    for _ in range(steps):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        variances.append(np.var(x))
    return np.mean(variances)

coupling_values = np.linspace(0.01, 0.99, 50)
spatial_variances = [calculate_spatial_variance(c) for c in coupling_values]

plt.figure(figsize=(10, 6))
plt.plot(coupling_values, spatial_variances, marker='o', linestyle='-')
plt.xlabel('Coupling Strength')
plt.ylabel('Average Spatial Variance')
plt.title('Transition Boundary: Coupling vs. Spatial Complexity')
plt.grid(True)
plt.savefig('transition_boundary.png')
