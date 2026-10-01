import numpy as np
from collections import Counter
from itertools import product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rules = {
    'Block': {'B': [], 'S': [2, 3]},
    'Block Glider': {'B': [3], 'S': [2, 3]},
    'Glider': {'B': [3], 'S': [2, 3]},
    'R-pentomino': {'B': [3], 'S': [2, 3]},
    'Random 30%': {'B': [], 'S': []},
}

fig, axes = plt.subplots(1, len(rules), figsize=(len(rules)*4, 4))
titles = []

for idx, r in enumerate(rules):
    grid = np.random.randint(0, 2, (40, 40))
    history = [grid]

    for _ in range(100):
        ng = np.zeros_like(grid)
        for i, j in product(range(40), repeat=2):
            nb = int(grid[(i-1)%40, j]) + int(grid[(i+1)%40, j]) + int(grid[i, (j-1)%40]) + int(grid[i, (j+1)%40])
            if grid[i, j] == 1 and nb in r['S']:
                ng[i, j] = 1
            elif grid[i, j] == 0 and nb in r['B']:
                ng[i, j] = 1
        grid = ng
        history.append(grid)

    densities = [np.mean(h) for h in history]
    axes[idx].plot(densities, label=f'Start={densities[0]:.2f}\nEnd={densities[-1]:.2f}', alpha=0.8)
    axes[idx].set_title(f'Rule {r} ({len(set(densities))})')
    axes[idx].set_xlabel('Time Step')
    axes[idx].set_ylabel('Density')
    axes[idx].legend()
    titles.append(f'Density Dynamics - Rule {r}')

plt.suptitle('\n'.join(titles), fontsize=10, y=1.02)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('conways_density_dynamics.png')
plt.close()