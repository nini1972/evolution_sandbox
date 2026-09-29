import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
use('Agg')
from ca_simulator import CellularAutomaton, lz_complexity

# Minimal parameters
GRID_SIZE = 40
STEPS = 100

# Initialize Conway's Game of Life
rules = {'B': [3], 'S': [2,3]}  # Conway rules
ca = CellularAutomaton(rules, size=GRID_SIZE)

# Run simulation (only spatial complexity)
spatial_entropy = []
for step in range(STEPS):
    ca.step()
    
    # Use cell density as lightweight complexity proxy
    spatial_entropy.append(np.mean(ca.grid))

# Generate visualizations
plt.figure(figsize=(10, 4))

# Final state
plt.subplot(121)
plt.imshow(ca.grid, cmap='binary')
plt.title('Final State')

# Spatial complexity
plt.subplot(122)
plt.plot(spatial_entropy)
plt.title('Spatial LZ Complexity')
plt.xlabel('Step')

plt.tight_layout()
plt.savefig('conway_complexity_local.png')

# Save metrics
with open('conway_metrics.txt', 'w') as f:
    f.write(f'Mean Spatial Complexity: {np.mean(spatial_entropy):.4f}\n')