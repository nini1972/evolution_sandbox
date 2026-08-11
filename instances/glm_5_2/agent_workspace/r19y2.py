import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 20
sigma = 5.0

fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#0a0a1a')
ax1, ax2 = axes
ax1.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')

K_values = np.arange(1, 45, 2.0)
dt_values = [0.1, 0.05, 0.02, 0.01]
colors = ['#ff4444', '#ff44aa', '#ffaa44', '#44ffcc']
markers = ['o', 's', '^', 'D']

for di, dt in enumerate(dt_values):
    n_steps = min(int(400 / dt), 20000)
    burn_in = int(n_steps * 0.5)
    sandpile_interval = max(1, int(0.1/dt))
    r_means = []
    
    for K in K_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        r_hist = []
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
                r_hist.append(abs(np.mean(np.exp(1j * theta))))
            if t % sandpile_interval == 0:
                dx, dy = np.random.randint(0, grid_size, 2)
                heights[dx, dy] += 1.0
                for _ in range(6):
                    u = heights >= threshold
                    if not u.any(): break
                    for x in range(grid_size):
                        for y in range(grid_size):
                            if heights[x,y] >= threshold[x,y]:
                                hd = threshold[x,y]
                                heights[x,y] -= hd
                                for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                                    if 0<=nx<grid_size and 0<=ny<grid_size:
                                        heights[nx,ny] += hd/4.0
        r_means.append(np.mean(r_hist))
    
    r_means = np.array(r_means)
    peak_r = np.max(r_means)
    final_r = r_means[-1]
    print(f"dt={dt}: peak={peak_r:.4f}, final={final_r:.4f}, decline={peak_r-final_r:.4f}")
    ax1.plot(K_values, r_means, f'{markers[di]}-', color=colors[di], linewidth=1.5, 
             markersize=4, label=f'dt={dt} (K_crit={2/dt:.0f})')

# Stability threshold lines
for dt, c in zip(dt_values, colors):
    ax1.axvline(x=2/dt, color=c, linestyle=':', alpha=0.3)

ax1.set_title('r(K) at Different Time Steps (sigma=5)', fontsize=14, color='#44ffcc')
ax1.set_xlabel('K', color='#e7e7f0')
ax1.set_ylabel('r', color='#e7e7f0')
ax1.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15)
ax1.set_ylim(0, 1.05)
ax1.annotate('Dotted lines: K_crit=2/dt\n(Euler stability limit)', xy=(30, 0.5), 
             fontsize=10, color='#ff44aa', bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#ff44aa', alpha=0.8))

# Panel 2: Stability diagram
K_r = np.linspace(0, 50, 200)
dt_r = np.linspace(0.005, 0.15, 200)
K_g, dt_g = np.meshgrid(K_r, dt_r)
stab = K_g * dt_g
ax2.contourf(K_g, dt_g, stab, levels=[0,1,2,3,5,10], colors=['#44ffcc','#44ffcc','#ffaa44','#ff4444','#660000'], alpha=0.7)
ax2.contour(K_g, dt_g, stab, levels=[2], colors='#ffffff', linewidths=2, linestyles='--')
ax2.set_title('Forward Euler Stability: K*dt < 2', fontsize=14, color='#44ffcc')
ax2.set_xlabel('K', color='#e7e7f0')
ax2.set_ylabel('dt', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.annotate('STABLE', xy=(5, 0.01), fontsize=16, color='#44ffcc', fontweight='bold')
ax2.annotate('UNSTABLE', xy=(30, 0.08), fontsize=16, color='#ff4444', fontweight='bold')

fig.suptitle('R19y: Numerical Stability Correction - "Over-coupling Decline" is an Integration Artifact', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_correction.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_correction.png')
