import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class JuliaExplorer:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.c = -0.8 + 0.156j  # Initial Julia set parameter
        self.x_min, self.x_max = -1.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5
        self.width, self.height = 400, 400
        self.ani = FuncAnimation(self.fig, self.update_julia_set, frames=50, interval=50, blit=True)

    def update_julia_set(self, frame):
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        z = x + 1j * y[:, None]
        mask = np.abs(z) < 2
        z[mask] = z[mask]**2 + self.c
        self.ax.clear()
        self.ax.imshow(~mask.T, cmap='jet', extent=(self.x_min, self.x_max, self.y_min, self.y_max))
        self.ax.set_title(f'Julia Set, c = {self.c:.3f}')
        return [self.ax.images[0]]