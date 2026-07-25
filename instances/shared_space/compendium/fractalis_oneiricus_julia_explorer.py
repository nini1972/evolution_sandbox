import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation

class JuliaExplorer:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.x_min, self.x_max = -1.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5
        self.width, self.height = 800, 600
        self.julia_set = np.zeros((self.height, self.width), dtype=np.uint8)
        self.im = ax.imshow(self.julia_set, cmap='inferno', extent=(self.x_min, self.x_max, self.y_min, self.y_max))
        
        # Add slider and button controls
        self.add_controls()
        
        self.ani = FuncAnimation(self.fig, self.update_julia_set, frames=50, interval=50, blit=True)
        
    def add_controls(self):
        # Add sliders for real and imaginary parts of c
        self.real_slider_ax = self.fig.add_axes([0.1, 0.05, 0.35, 0.03])
        self.real_slider = Slider(self.real_slider_ax, 'Real(c)', -1.5, 1.5, valinit=0.0, valstep=0.01)
        self.real_slider.on_changed(self.update_julia_parameters)
        
        self.imag_slider_ax = self.fig.add_axes([0.55, 0.05, 0.35, 0.03])
        self.imag_slider = Slider(self.imag_slider_ax, 'Imag(c)', -1.5, 1.5, valinit=0.0, valstep=0.01)
        self.imag_slider.on_changed(self.update_julia_parameters)
        
        # Add button for reset
        self.reset_button_ax = self.fig.add_axes([0.45, 0.01, 0.1, 0.05])
        self.reset_button = Button(self.reset_button_ax, 'Reset')
        self.reset_button.on_clicked(self.reset_view)
        
    def update_julia_parameters(self, val):
        self.c = self.real_slider.val + 1j * self.imag_slider.val
        self.fig.canvas.draw_idle()
        
    def reset_view(self, event):
        self.real_slider.reset()
        self.imag_slider.reset()
        self.update_julia_parameters(None)
        
    def update_julia_set(self, frame):
        # Update the Julia set
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        z = x + 1j * y[:, None]
        
        n = np.zeros_like(z, dtype=int)
        mask = np.ones_like(z, dtype=bool)
        for i in range(100):
            z[mask] = z[mask]**2 + self.c
            diverged = np.abs(z) > 2
            n[mask & diverged] = i
            mask &= ~diverged
        
        self.julia_set = n.T
        self.im.set_data(self.julia_set)
        return [self.im]