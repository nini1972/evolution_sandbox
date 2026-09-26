import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('robustness_results.json', 'r') as f:
    data = json.load(f)

plt.figure(figsize=(10, 6))
for size, entropies in data.items():
    plt.plot(entropies, label=f'Size {size}x{size}')

plt.title('Robustness of Entropy Convergence across Grid Sizes')
plt.xlabel('Generation')
plt.ylabel('Shannon Entropy')
plt.legend()
plt.grid(True)
plt.savefig('robustness_plot.png')
