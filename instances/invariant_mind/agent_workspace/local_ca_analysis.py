import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
use('Agg')
from ca_simulator import CellularAutomaton

# Parameters
GRID_SIZE = 80
STEPS = 300
WINDOW_SIZE = 10

# Initialize Conway's Game of Life
rules = {'B': [3], 'S': [2,3]}  # Conway rules
ca = CellularAutomaton(rules, size=GRID_SIZE)

# Run simulation
spatial_entropy, temporal_complexity = ca.simulate(STEPS, window_size=WINDOW_SIZE)

# Generate visualizations
plt.figure(figsize=(12, 6))

# Final state
plt.subplot(131)
plt.imshow(ca.grid, cmap='binary')
plt.title('Final State')

# Spatial complexity
plt.subplot(132)
plt.plot(spatial_entropy)
plt.title('Spatial LZ Complexity')
plt.xlabel('Step')

# Temporal complexity
plt.subplot(133)
plt.plot(temporal_complexity)
plt.title('Temporal LZ Complexity')
plt.xlabel(f'Step (window={WINDOW_SIZE})')

plt.tight_layout()
plt.savefig('conway_complexity_local.png')

# Save metrics
with open('conway_metrics.txt', 'w') as f:
    f.write(f'Mean Spatial Complexity: {np.mean(spatial_entropy):.4f}\n')
    f.write(f'Mean Temporal Complexity: {np.mean(temporal_complexity):.4f}\n')
    f.write(f'Complexity Ratio: {np.mean(spatial_entropy)/np.mean(temporal_complexity):.4f}')