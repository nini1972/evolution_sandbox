import numpy as np

class ReactionDiffusion:
    def __init__(self, size=50):
        self.size = size
        self.A = np.ones((size, size))
        self.B = np.zeros((size, size))
        self.B[size//2-5:size//2+5, size//2-5:size//2+5] = 1

    def laplacian(self, grid):
        return (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
                np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid)

    def evolve(self, dt=0.1, dA=1.0, dB=0.5, feed=0.055, kill=0.062):
        delta_A = (dA * self.laplacian(self.A) - self.A * self.B**2 + feed * (1 - self.A)) * dt
        delta_B = (dB * self.laplacian(self.B) + self.A * self.B**2 - (feed + kill) * self.B) * dt
        self.A += delta_A
        self.B += delta_B

rd = ReactionDiffusion()
for _ in range(50):
    rd.evolve()
print("RD step completed.")
