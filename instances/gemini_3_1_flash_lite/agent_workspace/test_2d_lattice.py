import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def run_2d_system(grid_size=20, c=0.2, steps=500):
    # Initial state
    x = np.random.rand(grid_size, grid_size)
    r = 3.6
    
    variances = []
    for _ in range(steps):
        x_next = r * x * (1 - x)
        
        # 2D 4-neighbor coupling
        x_coupled = (1 - c) * x_next + (c / 4) * (
            np.roll(x_next, 1, axis=0) + 
            np.roll(x_next, -1, axis=0) + 
            np.roll(x_next, 1, axis=1) + 
            np.roll(x_next, -1, axis=1)
        )
        x = x_coupled
        variances.append(np.var(x))
    return variances

variances = run_2d_system()
plt.figure(figsize=(10, 5))
plt.plot(variances)
plt.xlabel('Time Step')
plt.ylabel('Spatial Variance')
plt.title('Synchronization Stability in 2D Lattice')
plt.savefig('2d_lattice_stability.png')
