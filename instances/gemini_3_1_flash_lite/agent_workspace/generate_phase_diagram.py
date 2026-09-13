import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def calculate_spatial_lz(grid):
    # Flatten grid and convert to string to calculate Lempel-Ziv complexity
    # Simple proxy: number of unique patterns in the flattened data
    flat_grid = grid.flatten()
    s = "".join(map(str, flat_grid))
    n = len(s)
    if n == 0: return 0
    
    # Simple Lempel-Ziv complexity (number of unique substrings)
    # This is a placeholder for a more robust complexity metric
    complexity = len(set([s[i:i+3] for i in range(n-2)]))
    return complexity / (n - 2) if n > 2 else 0

def generate_system_state(size=50):
    # Simulate a system state (e.g., a simple CA-like grid)
    return np.random.choice([0, 1], size=(size, size), p=[0.7, 0.3])

# Collect data points for phase diagram
data = []
for _ in range(50):
    grid = generate_system_state()
    spatial_complexity = calculate_spatial_lz(grid)
    # Simulate temporal entropy decay as a random walk approximation
    temporal_entropy = np.random.rand() * (1 - spatial_complexity)
    data.append((spatial_complexity, temporal_entropy))

# Plot
data = np.array(data)
plt.figure(figsize=(10, 6))
plt.scatter(data[:, 0], data[:, 1], alpha=0.6)
plt.title("Spatiotemporal Phase Diagram: System Evolution")
plt.xlabel("Spatial Disorder (Block Entropy Proxy)")
plt.ylabel("Temporal Predictability (LZ Decay Proxy)")
plt.grid(True)
plt.savefig('spatiotemporal_phase_diagram.png')
print("Phase diagram generated as spatiotemporal_phase_diagram.png")
