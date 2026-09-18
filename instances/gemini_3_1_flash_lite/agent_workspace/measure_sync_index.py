import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def measure_sync(coupling, steps=200, size=100, r=3.949):
    x = np.random.rand(size)
    sync_indices = []
    for _ in range(steps):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        # Sync index: 1 - std of lattice state (normalized)
        sync_index = 1 - np.std(x)
        sync_indices.append(sync_index)
    return np.mean(sync_indices)

coupling_high = np.linspace(0.8, 1.0, 50)
sync_indices = [measure_sync(c) for c in coupling_high]

plt.figure(figsize=(10, 6))
plt.plot(coupling_high, sync_indices, marker='x', linestyle='--', color='red')
plt.xlabel('High Coupling Strength')
plt.ylabel('Synchronization Index')
plt.title('High-Coupling Synchronization Dynamics')
plt.grid(True)
plt.savefig('sync_dynamics.png')
