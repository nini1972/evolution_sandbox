import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation

class FractalisOneiricus:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.x_min, self.x_max = -2, 1
        self.y_min, self.y_max = -1.2, 1.2
        self.width, self.height = 800, 600
        self.mandelbrot = np.zeros((self.height, self.width), dtype=np.uint8)
        self.im = ax.imshow(self.mandelbrot, cmap='inferno', extent=(self.x_min, self.x_max, self.y_min, self.y_max))
        
        # Add slider and button controls
        self.add_controls()
        
        self.ani = FuncAnimation(self.fig, self.update_mandelbrot, frames=50, interval=50, blit=True)
        
    def add_controls(self):
        # Add slider for zoom
        self.zoom_slider_ax = self.fig.add_axes([0.1, 0.05, 0.8, 0.03])
        self.zoom_slider = Slider(self.zoom_slider_ax, 'Zoom', 1, 10, valinit=1, valstep=1)
        self.zoom_slider.on_changed(self.update_zoom)
        
        # Add button for reset
        self.reset_button_ax = self.fig.add_axes([0.45, 0.01, 0.1, 0.05])
        self.reset_button = Button(self.reset_button_ax, 'Reset')
        self.reset_button.on_clicked(self.reset_view)
        
    def update_zoom(self, val):
        zoom_factor = self.zoom_slider.val
        self.x_min = -2 / zoom_factor
        self.x_max = 1 / zoom_factor
        self.y_min = -1.2 / zoom_factor
        self.y_max = 1.2 / zoom_factor
        self.im.set_extent((self.x_min, self.x_max, self.y_min, self.y_max))
        self.fig.canvas.draw_idle()
        
    def reset_view(self, event):
        self.zoom_slider.reset()
        self.update_zoom(1)
        
    def update_mandelbrot(self, frame):
        # Update the Mandelbrot fractal
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        c = x + 1j * y[:, None]
        
        z = np.zeros_like(c)
        n = np.zeros_like(c, dtype=int)
        mask = np.ones_like(c, dtype=bool)
        for i in range(100):
            z[mask] = z[mask]**2 + c[mask]
            diverged = np.abs(z) > 2
            n[mask & diverged] = i
            mask &= ~diverged
        
        self.mandelbrot = n.T
        self.im.set_data(self.mandelbrot)
        return [self.im]