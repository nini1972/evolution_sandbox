import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Boid parameters
NUM_BOIDS = 30
FIELD_SIZE = 100

MAX_SPEED = 2.0
MAX_FORCE = 0.03

PERCEPTION_RADIUS = 15
SEPARATION_RADIUS = 8

# Weights for rules
SEP_WEIGHT = 1.5
ALI_WEIGHT = 1.0
COH_WEIGHT = 1.0

class Boid:
    def __init__(self):
        self.position = np.random.rand(2) * FIELD_SIZE
        self.velocity = (np.random.rand(2) - 0.5) * MAX_SPEED

    def update(self, boids):
        acceleration = self._apply_rules(boids)
        self.velocity += acceleration
        self._limit_speed()
        self.position += self.velocity
        self._wrap_around_edges()

    def _apply_rules(self, boids):
        separation = self._separation(boids)
        alignment = self._alignment(boids)
        cohesion = self._cohesion(boids)

        acceleration = (separation * SEP_WEIGHT +
                        alignment * ALI_WEIGHT +
                        cohesion * COH_WEIGHT)
        self._limit_force(acceleration)
        return acceleration

    def _separation(self, boids):
        steer = np.zeros(2)
        count = 0
        for other in boids:
            if other is not self:
                distance = np.linalg.norm(self.position - other.position)
                if distance < SEPARATION_RADIUS:
                    diff = self.position - other.position
                    steer += diff / distance # Weight by distance
                    count += 1
        if count > 0:
            steer /= count
            steer = self._set_magnitude(steer, MAX_SPEED)
            steer -= self.velocity
            self._limit_force(steer)
        return steer

    def _alignment(self, boids):
        avg_velocity = np.zeros(2)
        count = 0
        for other in boids:
            if other is not self:
                distance = np.linalg.norm(self.position - other.position)
                if distance < PERCEPTION_RADIUS:
                    avg_velocity += other.velocity
                    count += 1
        if count > 0:
            avg_velocity /= count
            avg_velocity = self._set_magnitude(avg_velocity, MAX_SPEED)
            steer = avg_velocity - self.velocity
            self._limit_force(steer)
            return steer
        return np.zeros(2)

    def _cohesion(self, boids):
        center_of_mass = np.zeros(2)
        count = 0
        for other in boids:
            if other is not self:
                distance = np.linalg.norm(self.position - other.position)
                if distance < PERCEPTION_RADIUS:
                    center_of_mass += other.position
                    count += 1
        if count > 0:
            center_of_mass /= count
            return self._seek(center_of_mass)
        return np.zeros(2)

    def _seek(self, target):
        desired = target - self.position
        desired = self._set_magnitude(desired, MAX_SPEED)
        steer = desired - self.velocity
        self._limit_force(steer)
        return steer

    def _limit_speed(self):
        if np.linalg.norm(self.velocity) > MAX_SPEED:
            self.velocity = self._set_magnitude(self.velocity, MAX_SPEED)

    def _limit_force(self, vector):
        if np.linalg.norm(vector) > MAX_FORCE:
            vector = self._set_magnitude(vector, MAX_FORCE)
        return vector

    def _set_magnitude(self, vector, magnitude):
        return vector / np.linalg.norm(vector) * magnitude if np.linalg.norm(vector) > 0 else np.zeros(2)

    def _wrap_around_edges(self):
        self.position[0] = self.position[0] % FIELD_SIZE
        self.position[1] = self.position[1] % FIELD_SIZE

# Initialize boids
boids = [Boid() for _ in range(NUM_BOIDS)]

# Setup plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, FIELD_SIZE)
ax.set_ylim(0, FIELD_SIZE)
ax.set_aspect('equal')

# Plot boids as points
scatter = ax.scatter([b.position[0] for b in boids], [b.position[1] for b in boids], s=10)

def animate(frame):
    for boid in boids:
        boid.update(boids)
    scatter.set_offsets([[b.position[0], b.position[1]] for b in boids])
    return scatter,

ani = FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
ani.save('../../shared_space/boids_flocking.gif', writer='pillow', dpi=100)

print("Boids flocking simulation generated and saved as boids_flocking.gif")
