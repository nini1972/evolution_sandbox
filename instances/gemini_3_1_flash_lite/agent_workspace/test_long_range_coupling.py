import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def run_small_world_system(size=50, c=0.3, steps=1000, spread=0.1, p=0.05):
    # Assign r values randomly around 3.6
    r_values = 3.6 + np.random.uniform(-spread, spread, size)
    x = np.random.rand(size)
    
    variances = []
    for _ in range(steps):
        x_next = r_values * x * (1 - x)
        
        # Local coupling
        x_coupled = (1 - c) * x_next + (c / 2) * (np.roll(x_next, 1) + np.roll(x_next, -1))
        
        # Add long-range coupling
        if np.random.rand() < p:
             # Random long-range link
             idx1, idx2 = np.random.randint(0, size, 2)
             x_coupled[idx1] = 0.5 * (x_coupled[idx1] + x_coupled[idx2])
             
        x = x_coupled
        variances.append(np.var(x))
    
    return variances

variances = run_small_world_system()
plt.figure(figsize=(12, 4))
plt.plot(variances)
plt.xlabel('Time Step')
plt.ylabel('Spatial Variance')
plt.title('Impact of Small-World Coupling on Heterogeneous Stability')
plt.savefig('long_range_coupling.png')
