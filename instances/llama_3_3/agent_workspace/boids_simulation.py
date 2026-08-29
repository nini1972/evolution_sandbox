import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Ensure matplotlib is using a non-interactive backend
plt.switch_backend('Agg')

class Boid:
    def __init__(self, x, y, vx, vy):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([vx, vy], dtype=float)

    def update(self):
        self.position += self.velocity

    def apply_rules(self, boids):
        v1 = self._separation(boids)
        v2 = self._alignment(boids)
        v3 = self._cohesion(boids)

        self.velocity += v1 + v2 + v3
        
        # Limit speed
        speed_limit = 5.0
        if np.linalg.norm(self.velocity) > speed_limit:
            self.velocity = (self.velocity / np.linalg.norm(self.velocity)) * speed_limit

    def _separation(self, boids):
        # Rule 1: Boids try to keep a small distance from other objects (including other boids).
        perception_radius = 20
        move = np.array([0.0, 0.0])
        for boid in boids:
            if boid is not self:
                distance = np.linalg.norm(self.position - boid.position)
                if distance < perception_radius:
                    move -= (boid.position - self.position) / distance  # Move away from crowded boids
        return move * 0.1 # Scaling factor

    def _alignment(self, boids):
        # Rule 2: Boids try to match velocity with near boids.
        perception_radius = 50
        avg_velocity = np.array([0.0, 0.0])
        num_neighbors = 0
        for boid in boids:
            if boid is not self:
                distance = np.linalg.norm(self.position - boid.position)
                if distance < perception_radius:
                    avg_velocity += boid.velocity
                    num_neighbors += 1
        if num_neighbors > 0:
            avg_velocity /= num_neighbors
            return (avg_velocity - self.velocity) * 0.05 # Scaling factor
        return avg_velocity

    def _cohesion(self, boids):
        # Rule 3: Boids try to fly towards the center of mass of neighboring boids.
        perception_radius = 50
        center_of_mass = np.array([0.0, 0.0])
        num_neighbors = 0
        for boid in boids:
            if boid is not self:
                distance = np.linalg.norm(self.position - boid.position)
                if distance < perception_radius:
                    center_of_mass += boid.position
                    num_neighbors += 1
        if num_neighbors > 0:
            center_of_mass /= num_neighbors
            return (center_of_mass - self.position) * 0.01 # Scaling factor
        return center_of_mass

def simulate_boids(num_boids, num_frames, x_lim, y_lim, filename="boids_flocking.gif"):
    boids = [Boid(np.random.rand() * x_lim, np.random.rand() * y_lim, 
                  np.random.uniform(-1, 1), np.random.uniform(-1, 1))
             for _ in range(num_boids)]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, x_lim)
    ax.set_ylim(0, y_lim)
    ax.set_title("Boids Flocking Simulation")
    
    # Plotting boids as points
    scat = ax.scatter([b.position[0] for b in boids], [b.position[1] for b in boids], s=10)

    def update(frame):
        current_positions = []
        for i, boid in enumerate(boids):
            # Apply rules first, then update position
            boid.apply_rules(boids) 
            boid.update()

            # Boundary conditions (wrap around)
            boid.position[0] %= x_lim
            boid.position[1] %= y_lim
            
            current_positions.append(boid.position)
            
        scat.set_offsets(current_positions)
        return scat,

    print(f"Generating Boids animation for {num_boids} boids over {num_frames} frames...")
    ani = FuncAnimation(fig, update, frames=num_frames, blit=True)
    ani.save(filename, writer='pillow', fps=20)
    print(f"Animation saved as {filename}")

if __name__ == "__main__":
    NUM_BOIDS = 20
    NUM_FRAMES = 100
    X_LIMIT = 200
    Y_LIMIT = 200
    simulate_boids(NUM_BOIDS, NUM_FRAMES, X_LIMIT, Y_LIMIT, filename=f"boids_{NUM_BOIDS}_boids_{NUM_FRAMES}_frames.gif")
