import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Objective function (e.g., Sphere function)
def objective_function(x):
    return np.sum(x**2, axis=-1)

# PSO parameters
NUM_PARTICLES = 30
NUM_DIMENSIONS = 2
MAX_ITERATIONS = 50

W = 0.5   # Inertia weight
C1 = 1.5  # Cognitive parameter (personal best)
C2 = 1.5  # Social parameter (global best)

# Search space bounds
LOWER_BOUND = -5
UPPER_BOUND = 5

# Initialize particles
positions = np.random.uniform(LOWER_BOUND, UPPER_BOUND, (NUM_PARTICLES, NUM_DIMENSIONS))
velocities = np.random.uniform(-1, 1, (NUM_PARTICLES, NUM_DIMENSIONS))

# Initialize personal bests
personal_best_positions = np.copy(positions)
personal_best_scores = np.array([objective_function(p) for p in positions])

# Initialize global best
global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
global_best_score = np.min(personal_best_scores)

# Store history for animation
history = []

# PSO main loop
for i in range(MAX_ITERATIONS):
    history.append(np.copy(positions)) # Store current positions

    # Update personal bests
    current_scores = np.array([objective_function(p) for p in positions])
    mask = current_scores < personal_best_scores
    personal_best_scores[mask] = current_scores[mask]
    personal_best_positions[mask] = positions[mask]

    # Update global best
    if np.min(current_scores) < global_best_score:
        global_best_score = np.min(current_scores)
        global_best_position = positions[np.argmin(current_scores)]

    # Update velocities and positions
    r1 = np.random.rand(NUM_PARTICLES, NUM_DIMENSIONS)
    r2 = np.random.rand(NUM_PARTICLES, NUM_DIMENSIONS)

    velocities = (W * velocities +
                  C1 * r1 * (personal_best_positions - positions) +
                  C2 * r2 * (global_best_position - positions))

    positions += velocities

    # Apply bounds to positions
    positions = np.clip(positions, LOWER_BOUND, UPPER_BOUND)


# Create animation
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(LOWER_BOUND, UPPER_BOUND)
ax.set_ylim(LOWER_BOUND, UPPER_BOUND)
ax.set_title("Particle Swarm Optimization")
ax.set_xlabel("Dimension 1")
ax.set_ylabel("Dimension 2")
ax.grid(True)

# Plot the objective function contours (for visualization)
x_vals = np.linspace(LOWER_BOUND, UPPER_BOUND, 100)
y_vals = np.linspace(LOWER_BOUND, UPPER_BOUND, 100)
X, Y = np.meshgrid(x_vals, y_vals)
Z = objective_function(np.stack([X, Y], axis=-1))
ax.contour(X, Y, Z, levels=20, cmap='viridis', alpha=0.7)


scatter = ax.scatter([], [], color='blue', s=50, alpha=0.8)
global_best_dot, = ax.plot([], [], 'o', color='red', markersize=10, label='Global Best')
ax.legend()

def update(frame):
    scatter.set_offsets(history[frame])
    # Update global best dot for each frame
    current_global_best_pos_in_frame = history[frame][np.argmin([objective_function(p) for p in history[frame]])]
    global_best_dot.set_data([current_global_best_pos_in_frame[0]], [current_global_best_pos_in_frame[1]])
    ax.set_title(f"Particle Swarm Optimization (Iteration: {frame+1}/{MAX_ITERATIONS})\nGlobal Best Score: {global_best_score:.4f}")
    return scatter, global_best_dot

ani = animation.FuncAnimation(fig, update, frames=len(history), blit=True)

# Save the animation as a GIF
ani.save('../../shared_space/pso_optimization.gif', writer='pillow', fps=10)

plt.close(fig)

print("PSO optimization animation generated and saved as pso_optimization.gif")
