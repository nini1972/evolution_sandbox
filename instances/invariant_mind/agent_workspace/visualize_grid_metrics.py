import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import convolve

# Load the grid data
grid_data = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
])

# Define the neighborhood kernel (Moore neighborhood)
kernel = np.array([
    [1, 1, 1],
    [1, 0, 1],
    [1, 1, 1]
])

# Function to calculate spatial entropy
# Spatial entropy measures the uncertainty or randomness in the spatial arrangement of cells
def calculate_spatial_entropy(grid):
    # Count the frequency of each cell value
    counts = np.bincount(grid.flatten())
    probabilities = counts / np.sum(counts)
    # Calculate Shannon entropy H(X) = -sum(p_i * log2(p_i))
    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    return entropy

# Function to calculate temporal complexity
# Temporal complexity measures the change in state over time
# Here, we count the number of unique states visited
def calculate_temporal_complexity(history):
    unique_states = set(tuple(state.flatten()) for state in history)
    return len(unique_states)

# Function to calculate pattern diversity
# Pattern diversity measures the variety of distinct patterns present
# We can extract connected components and count their types
from skimage.measure import label, regionprops

# Extract connected components
labeled_grid, num_features = label(grid_data, connectivity=2, return_num=True)

# Calculate pattern diversity based on the number of distinct component shapes
# Each regionprops object represents a distinct pattern
# We'll encode the shape as a tuple of coordinates
def calculate_pattern_diversity(labeled_grid, num_features):
    patterns = []
    for region in regionprops(labeled_grid):
        # Get the coordinates of the pattern
        row_coords, col_coords = region.coords[:, 0], region.coords[:, 1]
        # Sort and normalize coordinates to ensure consistent encoding
        sorted_coords = np.column_stack((row_coords, col_coords)).astype(float)
        sorted_coords -= sorted_coords.min(axis=0)
        sorted_coords /= sorted_coords.max(axis=0) * 100  # Scale to a small integer range
        patterns.append(tuple(sorted_coords.astype(int)))
    # Return the number of distinct patterns
    return len(set(patterns))

# Simulate the cellular automaton dynamics
# For demonstration, let's apply a simple rule: Any live cell with fewer than 2 neighbors dies,
# any live cell with 2 or 3 neighbors lives on, any live cell with more than 3 neighbors dies,
# and any dead cell with exactly 3 neighbors becomes alive
history = [grid_data]
for _ in range(10):  # Simulate for 10 time steps
    current_state = history[-1]
    # Convolve the current state with the kernel to get neighbor counts
    neighbor_counts = convolve(current_state, kernel, mode='constant', cval=0)
    # Apply the simple rule
    next_state = np.copy(current_state)
    next_state[(current_state == 1) & (neighbor_counts < 2)] = 0
    next_state[(current_state == 1) & ((neighbor_counts == 2) | (neighbor_counts == 3))] = 1
    next_state[(current_state == 1) & (neighbor_counts > 3)] = 0
    next_state[(current_state == 0) & (neighbor_counts == 3)] = 1
    history.append(next_state)

# Calculate metrics
spatial_entropy_history = [calculate_spatial_entropy(state) for state in history]
temporal_complexity = calculate_temporal_complexity(history)
pattern_diversity = calculate_pattern_diversity(labeled_grid, num_features)

# Visualize the results
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Plot 1: Spatial Entropy over time
axes[0].plot(spatial_entropy_history, marker='o', linestyle='-')
axes[0].set_title('Spatial Entropy Over Time')
axes[0].set_xlabel('Time Step')
axes[0].set_ylabel('Spatial Entropy')
axes[0].grid(True)

# Plot 2: Temporal Complexity
axes[1].bar(range(len(history)), [calculate_temporal_complexity([state]) for state in history]), color='skyblue')
axes[1].set_title('Temporal Complexity')
axes[1].set_xlabel('Time Step')
axes[1].set_ylabel('Unique States Visited')
axes[1].grid(True)

# Plot 3: Pattern Diversity
axes[2].bar(['Initial', 'After 10 Steps'], [pattern_diversity, calculate_pattern_diversity(label(np.array([[0,0],[0,0]]), connectivity=2)[0], 1)], color=['lightgreen', 'lightcoral'])
axes[2].set_title('Pattern Diversity')
axes[2].set_ylabel('Number of Distinct Patterns')
axes[2].grid(True, axis='y', alpha=0.7)

plt.suptitle('Metrics Visualization for 2D Grid Data', fontsize=16, fontweight='bold')
plt.tight_layout(pad=3.0)
plt.savefig('metrics_visualization.png')
print('Generated metrics_visualization.png')