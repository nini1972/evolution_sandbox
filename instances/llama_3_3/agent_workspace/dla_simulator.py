import numpy as np
import matplotlib.pyplot as plt
import random

# Simulation parameters
FIELD_SIZE = 100
NUM_PARTICLES = 1000
STICKING_PROBABILITY = 1.0 # For simplicity, all particles stick

# Create an empty grid
grid = np.zeros((FIELD_SIZE, FIELD_SIZE), dtype=int)

# Place the initial seed particle in the center
seed_x, seed_y = FIELD_SIZE // 2, FIELD_SIZE // 2
grid[seed_x, seed_y] = 1

# Function to check if a particle is adjacent to the aggregate
def is_adjacent_to_aggregate(x, y, current_grid):
    if current_grid[x, y] == 1: # Already part of aggregate
        return False
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: # 8 directions
        nx, ny = x + dx, y + dy
        if 0 <= nx < FIELD_SIZE and 0 <= ny < FIELD_SIZE and current_grid[nx, ny] == 1:
            return True
    return False

# Function to generate a random starting position on the edge of the field
def get_random_edge_position():
    side = random.choice([0, 1, 2, 3]) # 0:top, 1:bottom, 2:left, 3:right
    if side == 0: # top
        return 0, random.randint(0, FIELD_SIZE - 1)
    elif side == 1: # bottom
        return FIELD_SIZE - 1, random.randint(0, FIELD_SIZE - 1)
    elif side == 2: # left
        return random.randint(0, FIELD_SIZE - 1), 0
    else: # right
        return random.randint(0, FIELD_SIZE - 1), FIELD_SIZE - 1

# DLA simulation loop
for _ in range(NUM_PARTICLES):
    # Start a new walker from the edge
    px, py = get_random_edge_position()

    # Random walk until it hits the aggregate or goes too far
    while True:
        # Move randomly
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        npx, npy = px + dx, py + dy

        # Check boundaries
        if not (0 <= npx < FIELD_SIZE and 0 <= npy < FIELD_SIZE):
            # If it goes out of bounds, restart from edge
            px, py = get_random_edge_position()
            continue

        # Check if adjacent to aggregate
        if is_adjacent_to_aggregate(npx, npy, grid):
            if random.random() < STICKING_PROBABILITY:
                grid[npx, npy] = 1
                break # Particle stuck, move to next
            else:
                # If not sticking, restart from edge
                px, py = get_random_edge_position()
                continue

        px, py = npx, npy

# Visualization
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(grid, cmap='bone', origin='lower')
ax.set_title("Diffusion-Limited Aggregation (DLA)")
ax.axis('off')

plt.savefig('../../shared_space/dla_simulation.png')
plt.close()

print("DLA simulation generated and saved as dla_simulation.png")
