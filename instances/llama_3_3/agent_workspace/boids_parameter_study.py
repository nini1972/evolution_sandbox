import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# Boids parameters
NUM_BOIDS = 50
FIELD_SIZE = 100
MAX_SPEED = 2
MAX_FORCE = 0.05

# Rule distances
SEPARATION_RADIUS = 10
NEIGHBOR_RADIUS = 20

def calculate_separation(boid_id, boids_list):
    steer = np.zeros(2) # Initialize steer
    count = 0
    for i, other_boid in enumerate(boids_list):
        if i != boid_id:
            distance = np.linalg.norm(boids_list[boid_id, :2] - other_boid[:2])
            if distance < SEPARATION_RADIUS:
                diff = boids_list[boid_id, :2] - other_boid[:2]
                # Avoid division by zero if distance is extremely small
                if distance > 0: 
                    steer += diff / (distance**2) # Inverse square law for stronger repulsion closer by
                else: # Handle the case where boids are at the exact same position
                    steer += np.random.uniform(-1, 1, 2) * 100 # Random strong repulsion
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
        if np.linalg.norm(steer) > 0:
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

def run_boids_simulation(weight_separation, weight_alignment, weight_cohesion, filename):
    # Initialize boids: [x, y, vx, vy]
    boids = np.random.rand(NUM_BOIDS, 4) * FIELD_SIZE
    boids[:, 2:4] = (boids[:, 2:4] - 0.5) * 2 * MAX_SPEED # Random initial velocities

    def update_boids(boids_list):
        new_boids = np.copy(boids_list)
        for i in range(NUM_BOIDS):
            separation = calculate_separation(i, boids_list) * weight_separation
            alignment = calculate_alignment(i, boids_list) * weight_alignment
            cohesion = calculate_cohesion(i, boids_list) * weight_cohesion

            new_boids[i, 2:4] += separation + alignment + cohesion
            
            # Limit speed
            current_speed = np.linalg.norm(new_boids[i, 2:4])
            if current_speed > MAX_SPEED:
                new_boids[i, 2:4] = new_boids[i, 2:4] / current_speed * MAX_SPEED

            new_boids[i, :2] += new_boids[i, 2:4]

            # Wrap around edges
            new_boids[i, :2] %= FIELD_SIZE

        return new_boids

    # --- Animation setup ---
    fig, ax = plt.subplots(figsize=(8, 8))
    scatter = ax.scatter(boids[:, 0], boids[:, 1], s=10, color='blue')

    ax.set_xlim(0, FIELD_SIZE)
    ax.set_ylim(0, FIELD_SIZE)
    ax.set_title(f"Boids (S:{weight_separation}, A:{weight_alignment}, C:{weight_cohesion})")

    def animate(frame):
        nonlocal boids
        boids = update_boids(boids)
        scatter.set_offsets(boids[:, :2])
        return scatter,

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
    save_path = os.path.join('../../shared_space/', filename)
    ani.save(save_path, writer='pillow', fps=10)

    plt.close(fig)
    print(f"Simulation {filename} saved.")


# --- Parameter Study --- 
separation_weights = [0.5, 1.5, 2.5]
alignment_weights = [0.5, 1.0, 2.0]
cohesion_weights = [0.5, 1.0, 2.0]

# ... (existing report_content initialization)

report_content = "# Boids Parameter Study Report\n\n"
report_content += "This report details the emergent behaviors of Boids simulations under varying weights for separation, alignment, and cohesion.\n\n"

for ws in separation_weights:
    for wa in alignment_weights:
        for wc in cohesion_weights:
            sep_str = str(ws).replace(".", "_")
            align_str = str(wa).replace(".", "_")
            coh_str = str(wc).replace(".", "_")
            filename = f"boids_sep{sep_str}_align{align_str}_coh{coh_str}.gif"
            save_path = os.path.join('../../shared_space/', filename)

            report_content += f"## Separation: {ws}, Alignment: {wa}, Cohesion: {wc}\n"
            report_content += f"![Boids S:{ws} A:{wa} C:{wc}](../../shared_space/{filename})\n\n"

            # Check if the GIF already exists
            if os.path.exists(save_path):
                print(f"Skipping {filename} as it already exists.")
            else:
                run_boids_simulation(ws, wa, wc, filename)


with open('../../shared_space/boids_parameter_study_report.md', 'w') as f:
    f.write(report_content)

print("Boids parameter study complete. Report saved to boids_parameter_study_report.md")
