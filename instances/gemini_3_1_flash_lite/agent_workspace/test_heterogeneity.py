import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def run_heterogeneous_system(size=50, c=0.3, steps=1000, spread=0.1):
    # Assign r values randomly around 3.6
    r_values = 3.6 + np.random.uniform(-spread, spread, size)
    x = np.random.rand(size)
    
    variances = []
    for _ in range(steps):
        # Map update with local r
        x_next = r_values * x * (1 - x)
        # Apply coupling
        x = (1 - c) * x_next + (c / 2) * (np.roll(x_next, 1) + np.roll(x_next, -1))
        variances.append(np.var(x))
    
    return variances

variances = run_heterogeneous_system()
plt.figure(figsize=(12, 4))
plt.plot(variances)
plt.xlabel('Time Step')
plt.ylabel('Spatial Variance')
plt.title('Synchronization under Parameter Heterogeneity (Spread=0.1)')
plt.savefig('heterogeneity_impact.png')
