import numpy as np
from scipy.stats import entropy

def soliton_shape(x, v):
    gamma = 1 / np.sqrt(1 - v**2)
    return 1 / (np.cosh(gamma * x)**2)

results = {}
for v in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    x = np.linspace(-10, 10, 1000)
    shape = soliton_shape(x, v)
    shape /= np.sum(shape)
    results[v] = entropy(shape)

print(results)
