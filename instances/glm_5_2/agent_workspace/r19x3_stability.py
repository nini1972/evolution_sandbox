import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19x3: Stability Analysis - Is over-coupling real or numerical? ===')
np.random.seed(42)

grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 20
sigma = 5.0
T_sim = 600

# Test multiple dt values at high K to see if it's a numerical artifact
dt_values = [0.1, 0.05, 0.02, 0.01]
K_values = [10, 15, 20, 25, 30, 40]

fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

colors = ['#44ffcc', '#ff44aa', '#ffaa44', '#aaaaff']
markers = ['o', 's', '^', 'D']

for di, dt in enumerate(dt_values):
    print(f"  dt = {dt}")
    r_means = []
    
    n_steps = int(T_sim / dt)
    burn_in = int(300 / dt)
    
    for K in K_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        
        r_history = []
        
        for t in range(n_steps):
            sin_diff = np.sin(theta - theta[:, None])
            dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
            
            gx = np.random.randint(0, grid_size, N_osc)
            gy = np.random.randint(0, grid_size, N_osc)
            h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
            kicks = np.random.normal(0, sigma) * h_ratio
            dtheta += kicks
            theta = (theta + dtheta * dt) % (2*np.pi)
            
            if t > burn_in:
                r = np.abs(np.mean(np.exp(1j * theta)))
                r_history.append(r)
            
            # Sandpile (update every few steps proportional to dt)
            if t % max(1, int(0.1/dt)) == 0:
                drop_x, drop_y = np.random.randint(0, grid_size, 2)
                heights[drop_x, drop_y] += 1.0
                for _ in range(6):
                    unstable = heights >= threshold
                    if not unstable.any():
                        break
                    for x in range(grid_size):
                        for y in range(grid_size):
                            if heights[x, y] >= threshold[x, y]:
                                h_drop = threshold[x, y]
                                heights[x, y] -= h_drop
                                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                                    if 0 <= nx < grid_size and 0 <= ny < grid_size:
                                        heights[nx, ny] += h_drop / 4.0
        
        r_mean = np.mean(r_history)
        r_means.append(r_mean)
        print(f"    K={K:3d}: r={r_mean:.4f}")
    
    ax.plot(K_values, r_means, f'{markers[di]}-', color=colors[di], linewidth=2, 
            markersize=8, label=f'dt={dt}')

ax.set_title('Over-coupling Effect at Different Time Steps (sigma=5)', fontsize=14, color='#44ffcc')
ax.set_xlabel('K (coupling strength)', color='#e7e7f0')
ax.set_ylabel('r (order parameter)', color='#e7e7f0')
ax.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.15, color='#8a8aa3')
ax.set_ylim(0, 1.05)

# Add annotation
ax.annotate('If decline persists at smaller dt,\nit is a REAL dynamical effect\n(not numerical artifact)', 
            xy=(35, 0.7), fontsize=11, color='#ff44aa',
            bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#ff44aa', alpha=0.8))

fig.suptitle('R19x3: Numerical Stability Test for Over-coupling Decline', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_stability.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_stability.png')
print('=== R19x3 COMPLETE ===')
