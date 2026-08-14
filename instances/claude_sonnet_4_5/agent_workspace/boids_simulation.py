import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Boid class represents an individual agent
class Boid:
    def __init__(self, x, y, vx, vy, limits):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([vx, vy], dtype=float)
        self.limits = limits  # (min_x, max_x, min_y, max_y)

    def update(self, boids, separation_distance, alignment_strength, cohesion_strength, separation_strength, max_speed, avoidance_strength):
        # Calculate forces based on neighbors
        separation_force = self._separation(boids, separation_distance, separation_strength)
        alignment_force = self._alignment(boids, alignment_strength)
        cohesion_force = self._cohesion(boids, cohesion_strength)
        avoidance_force = self._keep_within_bounds(avoidance_strength)

        # Apply forces
        self.velocity += separation_force + alignment_force + cohesion_force + avoidance_force

        # Limit speed
        self._limit_speed(max_speed)

        # Update position
        self.position += self.velocity

        # Wrap around boundaries
        self._wrap_around_bounds()

    def _separation(self, boids, separation_distance, strength):
        # Rule 1: Separation - steer to avoid crowding local flockmates
        force = np.zeros(2)
        count = 0
        for other_boid in boids:
            if other_boid is not self:
                distance = np.linalg.norm(self.position - other_boid.position)
                if 0 < distance < separation_distance:
                    # Steer away from the boid
                    force += (self.position - other_boid.position) / (distance ** 2)  # Inverse square law for stronger repulsion closer
                    count += 1
        if count > 0:
            force /= count
        return force * strength

    def _alignment(self, boids, strength):
        # Rule 2: Alignment - steer towards the average heading of local flockmates
        average_velocity = np.zeros(2)
        count = 0
        for other_boid in boids:
            if other_boid is not self:
                average_velocity += other_boid.velocity
                count += 1
        if count > 0:
            average_velocity /= count
        return (average_velocity - self.velocity) * strength

    def _cohesion(self, boids, strength):
        # Rule 3: Cohesion - steer to move towards the average position of local flockmates
        average_position = np.zeros(2)
        count = 0
        for other_boid in boids:
            if other_boid is not self:
                average_position += other_boid.position
                count += 1
        if count > 0:
            average_position /= count
        return (average_position - self.position) * strength

    def _keep_within_bounds(self, strength):
        # Simple boundary avoidance, steering back towards the center
        force = np.zeros(2)
        min_x, max_x, min_y, max_y = self.limits
        if self.position[0] < min_x + 50:  # Within 50 units of left bound
            force[0] = strength
        elif self.position[0] > max_x - 50: # Within 50 units of right bound
            force[0] = -strength
        
        if self.position[1] < min_y + 50:  # Within 50 units of bottom bound
            force[1] = strength
        elif self.position[1] > max_y - 50: # Within 50 units of top bound
            force[1] = -strength
        return force

    def _limit_speed(self, max_speed):
        speed = np.linalg.norm(self.velocity)
        if speed > max_speed:
            self.velocity = (self.velocity / speed) * max_speed

    def _wrap_around_bounds(self):
        min_x, max_x, min_y, max_y = self.limits
        if self.position[0] < min_x: self.position[0] = max_x
        if self.position[0] > max_x: self.position[0] = min_x
        if self.position[1] < min_y: self.position[1] = max_y
        if self.position[1] > max_y: self.position[1] = min_y


# Simulation parameters
NUM_BOIDS = 50
FIELD_SIZE = 500
SIMULATION_STEPS = 100

# Boid behavior parameters
SEPARATION_DISTANCE = 20.0
MAX_SPEED = 5.0

# Strengths of the forces
SEPARATION_STRENGTH = 0.8
ALIGNMENT_STRENGTH = 0.05
COHESION_STRENGTH = 0.0005
AVOIDANCE_STRENGTH = 0.1

# Setup the simulation environment
limits = (0, FIELD_SIZE, 0, FIELD_SIZE)
boids = []
for _ in range(NUM_BOIDS):
    x = np.random.uniform(0, FIELD_SIZE)
    y = np.random.uniform(0, FIELD_SIZE)
    vx = np.random.uniform(-MAX_SPEED, MAX_SPEED) * 0.5 # Start with smaller random velocities
    vy = np.random.uniform(-MAX_SPEED, MAX_SPEED) * 0.5
    boids.append(Boid(x, y, vx, vy, limits))

# Setup for animation
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, FIELD_SIZE)
ax.set_ylim(0, FIELD_SIZE)
ax.set_aspect('equal', adjustable='box')
ax.set_title('Boids Flocking Simulation')

# Use scatter plot for boids
scat = ax.scatter([b.position[0] for b in boids], 
                  [b.position[1] for b in boids], 
                  s=10, c='blue')

def update_boids(frame):
    global boids
    for i, boid in enumerate(boids):
        # Pass all boids to each boid for force calculation
        boid.update(boids, SEPARATION_DISTANCE, ALIGNMENT_STRENGTH, COHESION_STRENGTH, SEPARATION_STRENGTH, MAX_SPEED, AVOIDANCE_STRENGTH)

    # Update scatter plot data
    scat.set_offsets(np.array([[b.position[0], b.position[1]] for b in boids]))
    return scat,

print("Generating Boids animation...")
ani = FuncAnimation(fig, update_boids, frames=SIMULATION_STEPS, blit=True, interval=50)
ani.save('boids_flocking.gif', writer='pillow', fps=20)
print("Boids animation saved as boids_flocking.gif")

plt.close(fig)
