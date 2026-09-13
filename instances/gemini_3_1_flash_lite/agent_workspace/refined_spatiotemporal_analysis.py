import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def calculate_lz_complexity(s):
    # Standard Lempel-Ziv complexity: number of unique patterns
    n = len(s)
    if n == 0: return 0
    
    i = 0
    count = 0
    patterns = set()
    while i < n:
        found = False
        for j in range(i+1, n+1):
            sub = s[i:j]
            if sub not in patterns:
                patterns.add(sub)
                count += 1
                i = j
                found = True
                break
        if not found:
            i += 1
    return count

def generate_ca_dynamics(size=50, steps=100):
    # Rule 30-like local evolution simulation
    grid = np.random.choice([0, 1], size=(size, size))
    history = []
    for _ in range(steps):
        history.append(grid.copy())
        new_grid = np.zeros_like(grid)
        # Simplified rule 30
        for i in range(1, size-1):
            for j in range(1, size-1):
                new_grid[i, j] = grid[i-1, j] ^ (grid[i, j+1] | grid[i+1, j])
        grid = new_grid
    return history

def analyze_dynamics(history):
    spatial_complexities = []
    temporal_complexities = []
    
    # Spatial: average LZ over a frame
    for frame in history:
        s = "".join(map(str, frame.flatten()))
        spatial_complexities.append(calculate_lz_complexity(s))
        
    # Temporal: LZ of a specific pixel's history
    for i in range(5):
        s = "".join(map(str, [history[t][25, 25] for t in range(len(history))]))
        temporal_complexities.append(calculate_lz_complexity(s))
        
    return np.mean(spatial_complexities), np.mean(temporal_complexities)

# Main execution
results = []
for _ in range(20):
    history = generate_ca_dynamics()
    spatial, temporal = analyze_dynamics(history)
    results.append((spatial, temporal))

results = np.array(results)
plt.figure(figsize=(10, 6))
plt.scatter(results[:, 0], results[:, 1], color='purple', alpha=0.7)
plt.title("Canonical Spatiotemporal Phase Map (Refined)")
plt.xlabel("Spatial Complexity (LZ)")
plt.ylabel("Temporal Complexity (LZ)")
plt.grid(True)
plt.savefig('refined_spatiotemporal_phase_diagram.png')
print("Refined phase diagram generated as refined_spatiotemporal_phase_diagram.png")
