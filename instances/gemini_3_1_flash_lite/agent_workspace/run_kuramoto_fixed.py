import numpy as np
import json

def kuramoto_sync(N=100, K=2.0, t_steps=500):
    # Fixed seed for reproducibility
    np.random.seed(42)
    phases = np.random.uniform(0, 2*np.pi, N)
    freqs = np.random.normal(0, 1, N)
    
    # Integration
    for _ in range(t_steps):
        d_phases = freqs + (K/N) * np.sum(np.sin(phases[:, None] - phases), axis=1)
        phases += d_phases * 0.01
    
    r = np.abs(np.mean(np.exp(1j * phases)))
    return r

results = {str(K): float(kuramoto_sync(K=K)) for K in np.linspace(0, 4, 20)}
with open('kuramoto_sync_results.json', 'w') as f:
    json.dump(results, f)
