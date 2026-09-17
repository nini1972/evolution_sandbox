import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def cml_time_series(size=100, steps=500, coupling=0.1, r=3.8):
    x = np.random.rand(size)
    history = []
    for _ in range(steps):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        history.append(np.mean(x))
    return np.array(history)

# Analyze PSD for two different coupling values
c1 = cml_time_series(coupling=0.01)
c2 = cml_time_series(coupling=0.5)

plt.figure(figsize=(10, 5))
plt.psd(c1, Fs=1, label='Low Coupling (0.01)')
plt.psd(c2, Fs=1, label='High Coupling (0.5)')
plt.legend()
plt.title('Power Spectral Density Comparison')
plt.savefig('spectral_symmetry_analysis.png')
