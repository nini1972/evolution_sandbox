from colony_lib.dynamics import Kuramoto
import numpy as np
import json

# Setup: N oscillators, random natural frequencies
N = 100
t_max = 50
dt = 0.1
# Sweep coupling strength K
K_values = np.linspace(0, 5, 20)
order_parameters = []

for K in K_values:
    # Simplified Kuramoto call (assuming the library structure)
    model = Kuramoto(N=N, K=K, coupling='mean_field')
    # Simulate
    history = model.simulate(t_max=t_max, dt=dt)
    # Calculate order parameter R (average phase synchronization)
    R = model.calculate_order_parameter(history[-1])
    order_parameters.append(float(R))

results = {float(K): float(R) for K, R in zip(K_values, order_parameters)}
with open('kuramoto_sync_results.json', 'w') as f:
    json.dump(results, f)
