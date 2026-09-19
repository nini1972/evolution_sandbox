import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_spectrum(coupling=0.3, size=128, steps=1000, r=3.949):
    x = np.random.rand(size)
    # Run to a steady state
    for _ in range(500):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
    
    # Compute power spectrum
    fft = np.fft.fft(x)
    spectrum = np.abs(fft)**2
    return spectrum[:size//2]

spectrum = get_spectrum()

plt.figure(figsize=(10, 6))
plt.loglog(spectrum, marker='.', linestyle='none')
plt.xlabel('Spatial Frequency (k)')
plt.ylabel('Power Spectrum')
plt.title('Spatial Power Spectrum (Coupling=0.3)')
plt.grid(True)
plt.savefig('spatial_spectrum.png')
