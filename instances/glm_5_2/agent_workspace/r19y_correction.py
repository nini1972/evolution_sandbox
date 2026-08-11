import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19y: Corrected Analysis - Numerical Stability vs Real Dynamics ===')
np.random.seed(42)

grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 20
sigma = 5.0

# Stability criterion for forward Euler on Kuramoto:
# The linearized system near sync has eigenvalues ~ -K (for the fastest mode)
# Forward Euler stability requires: dt * |lambda_max| < 2
# So: dt * K < 2, i.e., K < 2/dt

# Create comprehensive comparison plot
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#0a0a1a')
ax1, ax2 = axes
ax1.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')

K_values = np.arange(1, 45, 1.0)
dt_values = [0.1, 0.05, 0.02, 0.01]
colors = ['#ff4444', '#ff44aa', '#ffaa44', '#44ffcc']
markers = ['o', 's', '^', 'D']

for di, dt in enumerate(dt_values):
    print(f"  dt = {dt}")
    r_means = []
    n_steps = min(int(600 / dt), 30000)
    burn_in = int(n_steps * 0.5)
    sandpile_interval = max(1, int(0.1/dt))
    
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
            
            if t % sandpile_interval == 0:
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
        
        r_means.append(np.mean(r_history))
    
    r_means = np.array(r_means)
    ax1.plot(K_values, r_means, f'{markers[di]}-', color=colors[di], linewidth=1.5, 
             markersize=4, label=f'dt={dt} (K_crit={2/dt:.0f})')
    
    # Print decline
    if len(r_means) > 10:
        peak_r = np.max(r_means)
        final_r = r_means[-1]
        print(f"    Peak r={peak_r:.4f}, Final r={final_r:.4f}, Decline={peak_r-final_r:.4f}")

# Add stability threshold lines
for dt in dt_values:
    K_crit = 2 / dt
    ax1.axvline(x=K_crit, color=colors[dt_values.index(dt)], linestyle=':', alpha=0.3, linewidth=1)

ax1.set_title('r(K) at Different Time Steps (sigma=5)', fontsize=14, color='#44ffcc')
ax1.set_xlabel('K (coupling strength)', color='#e7e7f0')
ax1.set_ylabel('r (order parameter)', color='#e7e7f0')
ax1.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15, color='#8a8aa3')
ax1.set_ylim(0, 1.05)
ax1.annotate('Vertical lines: K_crit = 2/dt\n(Euler stability limit)', 
             xy=(30, 0.5), fontsize=10, color='#ff44aa',
             bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#ff44aa', alpha=0.8))

# Panel 2: Stability diagram
K_range = np.linspace(0, 50, 200)
dt_range = np.linspace(0.005, 0.15, 200)
K_grid, dt_grid = np.meshgrid(K_range, dt_range)
stability = K_grid * dt_grid  # K*dt product
# Stable if K*dt < 2
stable_mask = stability < 2

ax2.contourf(K_grid, dt_grid, stability, levels=[0, 1, 2, 3, 5, 10], 
             colors=['#44ffcc', '#44ffcc', '#ffaa44', '#ff4444', '#660000'], alpha=0.7)
ax2.contour(K_grid, dt_grid, stability, levels=[2], colors='#ffffff', linewidths=2, linestyles='--')
ax2.set_title('Forward Euler Stability: K * dt < 2', fontsize=14, color='#44ffcc')
ax2.set_xlabel('K (coupling strength)', color='#e7e7f0')
ax2.set_ylabel('dt (time step)', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.annotate('STABLE', xy=(5, 0.01), fontsize=16, color='#44ffcc', fontweight='bold')
ax2.annotate('UNSTABLE', xy=(30, 0.08), fontsize=16, color='#ff4444', fontweight='bold')
ax2.plot([0, 50], [0.1, 0.1], 'w-', alpha=0.5, linewidth=1)  # dt=0.1 line

fig.suptitle('R19y: Numerical Stability Correction - The "Over-coupling Decline" is an Integration Artifact', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_correction.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_correction.png')
print('=== R19y COMPLETE ===')
