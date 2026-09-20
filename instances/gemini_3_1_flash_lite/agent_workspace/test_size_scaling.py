import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_peak_frequency(size, r=3.9, c=0.3, steps=1024):
    x = np.random.rand(size)
    variances = []
    # Burn-in
    for _ in range(500):
        x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
    
    # Capture
    for _ in range(steps):
        x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        variances.append(np.var(x))
    
    fft_vals = np.abs(np.fft.rfft(variances))
    # Return frequency of maximum power
    return np.argmax(fft_vals[1:]) + 1

sizes = [10, 20, 40, 80, 160]
freqs = [get_peak_frequency(s) for s in sizes]

plt.figure(figsize=(8, 5))
plt.plot(sizes, freqs, 'o-')
plt.xlabel('Lattice Size (N)')
plt.ylabel('Peak Frequency (Synchronization Instability)')
plt.title('Scaling of Phase-Slip Frequency with System Size')
plt.grid(True)
plt.savefig('size_scaling.png')
