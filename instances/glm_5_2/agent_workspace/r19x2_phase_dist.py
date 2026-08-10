import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19x2: Phase Distribution at High K ===')
np.random.seed(42)

grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
dt = 0.1
N_osc = 20
T_sim = 1000
sigma = 5.0

K_values = [3, 5, 10, 15, 20, 30, 40]

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.patch.set_facecolor('#0a0a1a')
axes = axes.flatten()

for ki, K in enumerate(K_values):
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    
    phase_snapshots = []
    r_history = []
    
    for t in range(T_sim):
        sin_diff = np.sin(theta - theta[:, None])
        dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
        
        gx = np.random.randint(0, grid_size, N_osc)
        gy = np.random.randint(0, grid_size, N_osc)
        h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
        kicks = np.random.normal(0, sigma) * h_ratio
        dtheta += kicks
        theta = (theta + dtheta * dt) % (2*np.pi)
        
        if t > 500:
            r = np.abs(np.mean(np.exp(1j * theta)))
            r_history.append(r)
            if t % 100 == 0:
                phase_snapshots.append(theta.copy())
        
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
    r_std = np.std(r_history)
    
    # Plot histogram of phases (relative to mean phase)
    all_phases = []
    for snap in phase_snapshots:
        mean_phase = np.angle(np.mean(np.exp(1j * snap)))
        rel_phases = np.angle(np.exp(1j * (snap - mean_phase)))
        all_phases.extend(rel_phases)
    
    ax = axes[ki]
    ax.set_facecolor('#0a0a1a')
    ax.hist(all_phases, bins=30, color='#44ffcc', alpha=0.7, edgecolor='#1a1a2a')
    ax.set_title(f'K={K}, r={r_mean:.3f}±{r_std:.3f}', color='#44ffcc', fontsize=12)
    ax.set_xlabel('Phase relative to mean', color='#8a8aa3', fontsize=10)
    ax.set_ylabel('Count', color='#8a8aa3', fontsize=10)
    ax.tick_params(colors='#8a8aa3')
    ax.set_xlim(-np.pi, np.pi)
    
    # Also measure phase variance
    phase_var = np.var(all_phases)
    print(f"  K={K:3d}: r={r_mean:.4f}, r_std={r_std:.4f}, phase_var={phase_var:.4f}, n_snaps={len(phase_snapshots)}")

# Hide the 8th subplot
axes[7].set_visible(False)

fig.suptitle(f'R19x2: Phase Distribution at Different K (sigma={sigma})', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_phase_dist.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_phase_dist.png')
print('=== R19x2 COMPLETE ===')
