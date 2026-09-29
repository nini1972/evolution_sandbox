import numpy as np
from scipy.stats import entropy

def soliton_shape(x, v):
    # Relativistic soliton profile (simplified)
    gamma = 1 / np.sqrt(1 - v**2)
    return 1 / (np.cosh(gamma * x)**2)

x = np.linspace(-10, 10, 100)
results = []
for v in np.linspace(0.01, 0.99, 50):
    shape = soliton_shape(x, v)
    # Normalize for entropy calculation
    shape /= np.sum(shape)
    results.append(entropy(shape))

print(f"Mean Entropy: {np.mean(results)}")
print(f"Variance: {np.var(results)}")
