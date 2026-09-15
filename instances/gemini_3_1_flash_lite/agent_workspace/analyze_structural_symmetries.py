import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.fft import fft2

def cml_spatial_series(size=100, steps=200, coupling=0.1, r=3.8):
    x = np.random.rand(size)
    history = np.zeros((steps, size))
    for i in range(steps):
        history[i, :] = x
        x_next = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        x = x_next
    return history

def analyze_symmetries(data):
    # Perform 2D FFT to identify spatial and temporal periodicities (symmetries)
    f_transform = np.abs(fft2(data))
    return f_transform

# Generate and analyze
data = cml_spatial_series(size=128, steps=128, coupling=0.1, r=3.8)
spectrum = analyze_symmetries(data)

plt.imshow(np.log1p(spectrum), cmap='magma')
plt.colorbar(label='Log Spectral Magnitude')
plt.title('Spectral Symmetry Analysis (r=3.8, c=0.1)')
plt.savefig('spectral_symmetry_analysis.png')
print("Spectral analysis completed.")
