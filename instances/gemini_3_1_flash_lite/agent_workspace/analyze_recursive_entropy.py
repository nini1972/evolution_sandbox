import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('recursive_evolution.json', 'r') as f:
    data = json.load(f)
history = np.array(data['history'])

entropies = []
for grid in history:
    # Estimate Shannon entropy for binary grid
    p = np.mean(grid)
    if p == 0 or p == 1:
        entropy = 0
    else:
        entropy = - (p * np.log2(p) + (1-p) * np.log2(1-p))
    entropies.append(entropy)

plt.figure(figsize=(10, 5))
plt.plot(entropies)
plt.title('Shannon Entropy over Generations (Recursive CA)')
plt.xlabel('Generation')
plt.ylabel('Entropy')
plt.grid(True)
plt.savefig('recursive_entropy_plot.png')
