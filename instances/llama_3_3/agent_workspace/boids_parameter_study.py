import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Boids parameters
NUM_BOIDS = 50
FIELD_SIZE = 100
MAX_SPEED = 2
MAX_FORCE = 0.05

# Rule weights (these will be varied in the study)
WEIGHT_SEPARATION = 1.5
WEIGHT_ALIGNMENT = 1.0
WEIGHT_COHESION = 1.0

# Rule distances
SEPARATION_RADIUS = 10
NEIGHBOR_RADIUS = 20

# Initialize boids: [x, y, vx, vy]
boids = np.random.rand(NUM_BOIDS, 4) * FIELD_SIZE
boids[:, 2:4] = (boids[:, 2:4] - 0.5) * 2 * MAX_SPEED # Random initial velocities

def calculate_separation(boid_id, boids_list):
    steer = np.zeros(2) # Initialize steer
    count = 0
    for i, other_boid in enumerate(boids_list):
        if i != boid_id:
            distance = np.linalg.norm(boids_list[boid_id, :2] - other_boid[:2])
            if distance < SEPARATION_RADIUS:
                diff = boids_list[boid_id, :2] - other_boid[:2]
                steer += diff / (distance**2) # Inverse square law for stronger repulsion closer by
                count += 1
    if count > 0:
        steer /= count
        if np.linalg.norm(steer) > 0:
            steer = steer / np.linalg.norm(steer) * MAX_SPEED
            steer -= boids_list[boid_id, 2:4]
            steer = np.clip(steer, -MAX_FORCE, MAX_FORCE)
    return steer

def calculate_alignment(boid_id, boids_list):
    steer = np.zeros(2) # Initialize steer
    count = 0
    for i, other_boid in enumerate(boids_list):
        if i != boid_id:
            distance = np.linalg.norm(boids_list[boid_id, :2] - other_boid[:2])
            if distance < NEIGHBOR_RADIUS:
                steer += other_boid[2:4] # Sum velocities of neighbors
                count += 1
    if count > 0:
        steer /= count
        steer = steer / np.linalg.norm(steer) * MAX_SPEED
        steer -= boids_list[boid_id, 2:4]
        steer = np.clip(steer, -MAX_FORCE, MAX_FORCE)
    return steer

def calculate_cohesion(boid_id, boids_list):
    center_of_mass = np.zeros(2)
    steer = np.zeros(2) # Initialize steer
    count = 0
    for i, other_boid in enumerate(boids_list):
        if i != boid_id:
            distance = np.linalg.norm(boids_list[boid_id, :2] - other_boid[:2])
            if distance < NEIGHBOR_RADIUS:
                center_of_mass += other_boid[:2] # Sum positions of neighbors
                count += 1
    if count > 0:
        center_of_mass /= count
        steer = center_of_mass - boids_list[boid_id, :2]
        if np.linalg.norm(steer) > 0:
            steer = steer / np.linalg.norm(steer) * MAX_SPEED
            steer -= boids_list[boid_id, 2:4]
            steer = np.clip(steer, -MAX_FORCE, MAX_FORCE)
    return steer

def update_boids(boids_list):
    new_boids = np.copy(boids_list)
    for i in range(NUM_BOIDS):
        separation = calculate_separation(i, boids_list) * WEIGHT_SEPARATION
        alignment = calculate_alignment(i, boids_list) * WEIGHT_ALIGNMENT
        cohesion = calculate_cohesion(i, boids_list) * WEIGHT_COHESION

        new_boids[i, 2:4] += separation + alignment + cohesion
        
        # Limit speed
        if np.linalg.norm(new_boids[i, 2:4]) > MAX_SPEED:
            new_boids[i, 2:4] = new_boids[i, 2:4] / np.linalg.norm(new_boids[i, 2:4]) * MAX_SPEED

        new_boids[i, :2] += new_boids[i, 2:4]

        # Wrap around edges
        new_boids[i, :2] %= FIELD_SIZE

    return new_boids

# --- Animation setup (for a single run) ---
fig, ax = plt.subplots(figsize=(8, 8))
scatter = ax.scatter(boids[:, 0], boids[:, 1], s=10, color='blue')

ax.set_xlim(0, FIELD_SIZE)
ax.set_ylim(0, FIELD_SIZE)
ax.set_title("Boids Flocking Simulation")

def animate(frame):
    global boids
    boids = update_boids(boids)
    scatter.set_offsets(boids[:, :2])
    return scatter,

ani = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=True)
ani.save('../../shared_space/boids_flocking_default.gif', writer='pillow', fps=20)

plt.close(fig)

print("Default Boids flocking animation saved as boids_flocking_default.gif")
