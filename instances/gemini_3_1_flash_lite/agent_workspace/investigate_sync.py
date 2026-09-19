import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def get_sync_metrics(coupling_range, r=3.9, size=50, steps=1000):
    sync_errors = []
    for c in coupling_range:
        x = np.random.rand(size)
        # Steady state
        for _ in range(500):
            x = (1 - c) * (r * x * (1 - x)) + (c / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        
        # Measure variance across space: lower variance -> higher synchronization
        sync_errors.append(np.var(x))
    return sync_errors

c_vals = np.linspace(0.0, 0.6, 100)
sync_data = get_sync_metrics(c_vals)

plt.figure(figsize=(10, 6))
plt.plot(c_vals, sync_data)
plt.xlabel('Coupling Strength')
plt.ylabel('Spatial Variance (Synchronization Error)')
plt.title('Synchronization Transition: Coupling vs Global Spatial Coherence')
plt.grid(True)
plt.savefig('sync_transition.png')
