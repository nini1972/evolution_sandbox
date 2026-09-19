import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def monitor_variance(r=3.9, c=0.3, size=50, total_steps=1000):
    x = np.random.rand(size)
    variances = []
    for _ in range(total_steps):
        x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        variances.append(np.var(x))
    return variances

variances = monitor_variance()
plt.figure(figsize=(12, 4))
plt.plot(variances)
plt.xlabel('Time Step')
plt.ylabel('Spatial Variance')
plt.title('Temporal Dynamics of Synchronization Error (c=0.3)')
plt.savefig('phase_slip_monitoring.png')

# Also save the Fourier Transform of the variance to find oscillation frequencies
fft_freqs = np.abs(np.fft.rfft(variances))
plt.figure(figsize=(12, 4))
plt.plot(fft_freqs[1:]) # Skip DC component
plt.xlabel('Frequency Component')
plt.ylabel('Magnitude')
plt.title('Spectral Decomposition of Synchronization Error')
plt.savefig('sync_error_spectrum.png')
