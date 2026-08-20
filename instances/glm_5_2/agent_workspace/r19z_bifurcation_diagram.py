import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 40.0
dt = 0.02
burn_frac = 0.2
sandpile_interval = max(1, int(0.1 / dt))
n_steps = int(total_time / dt)
burn_in = int(n_steps * burn_frac)

def kuramoto_rhs(theta, omega, K, N):
    sin_diff = np.sin(theta - theta[:, None])
    return omega + (K / N) * sin_diff.sum(axis=1)

def get_kicks(sigma, heights, threshold, N):
    gx = np.random.randint(0, grid_size, N)
    gy = np.random.randint(0, grid_size, N)
    h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
    return np.random.normal(0, sigma) * h_ratio

def sandpile_step(heights, threshold, n_relax=3):
    dx, dy = np.random.randint(0, grid_size, 2)
    heights[dx, dy] += 1.0
    for _ in range(n_relax):
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
    return heights

sigma = 100
alpha = 0.9
K_values = np.arange(4, 31, 1.0)
all_r_samples = []

print(f"Running {len(K_values)} K values, {n_steps} steps each...")

for ki, K in enumerate(K_values):
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    r_hist = []
    
    for t in range(n_steps):
        r = abs(np.mean(np.exp(1j * theta)))
        threshold = base_threshold * (1.0 - alpha * r)
        threshold = np.maximum(threshold, 0.3)
        noise = get_kicks(sigma, heights, threshold, N_osc)
        k1 = kuramoto_rhs(theta, omega, K, N_osc) + noise
        k2 = kuramoto_rhs(theta + 0.5*dt*k1, omega, K, N_osc) + noise
        k3 = kuramoto_rhs(theta + 0.5*dt*k2, omega, K, N_osc) + noise
        k4 = kuramoto_rhs(theta + dt*k3, omega, K, N_osc) + noise
        theta = (theta + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)) % (2*np.pi)
        if t > burn_in:
            r_hist.append(r)
        if t % sandpile_interval == 0:
            heights = sandpile_step(heights, threshold)
    
    r_arr = np.array(r_hist)
    samples = r_arr[::3]
    all_r_samples.append(samples)
    print(f"  K={K:.0f}: r_mean={np.mean(r_arr):.3f}, r_std={np.std(r_arr):.3f}")

# Plot bifurcation diagram
fig, ax = plt.subplots(figsize=(18, 10))
for ki, K in enumerate(K_values):
    samples = all_r_samples[ki]
    ax.scatter(np.full(len(samples), K), samples, s=0.5, c='cyan', alpha=0.3, marker=',')

ax.set_xlabel('Coupling K', fontsize=14)
ax.set_ylabel('Order parameter r(t)', fontsize=14)
ax.set_title(f'R19Z: Bifurcation Diagram — r(t) distribution vs K\n'
             f'α={alpha}, σ={sigma}, {len(K_values)} K values',
             fontsize=14, fontweight='bold')
ax.set_xlim(K_values[0]-0.5, K_values[-1]+0.5)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.2)
ax.tick_params(labelsize=12)

plt.tight_layout()
fig.savefig('r19z_bifurcation_diagram.png', dpi=150, bbox_inches='tight')
print("Saved r19z_bifurcation_diagram.png")

# Stats
r_means = [np.mean(s) for s in all_r_samples]
r_stds = [np.std(s) for s in all_r_samples]
r_cvs = [np.std(s)/(np.mean(s)+1e-10) for s in all_r_samples]

fig2, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
fig2.suptitle(f'R19Z: Statistical Analysis of r(t) vs K (α={alpha}, σ={sigma})',
              fontsize=14, fontweight='bold')

ax1.plot(K_values, r_means, 'o-', markersize=5, color='blue')
ax1.fill_between(K_values,
                  [m-s for m,s in zip(r_means, r_stds)],
                  [m+s for m,s in zip(r_means, r_stds)],
                  alpha=0.2, color='blue')
ax1.set_ylabel('Mean r(t) ± std', fontsize=12)
ax1.grid(True, alpha=0.3)

ax2.plot(K_values, r_stds, 'o-', markersize=5, color='red')
ax2.set_ylabel('Std of r(t)', fontsize=12)
ax2.grid(True, alpha=0.3)

ax3.plot(K_values, r_cvs, 'o-', markersize=5, color='green')
ax3.set_ylabel('Coefficient of Variation', fontsize=12)
ax3.set_xlabel('Coupling K', fontsize=12)
ax3.grid(True, alpha=0.3)
ax3.axhline(y=0.1, color='gray', linestyle='--', alpha=0.5, label='CV=0.1 threshold')
ax3.legend()

plt.tight_layout()
fig2.savefig('r19z_bifurcation_stats.png', dpi=150, bbox_inches='tight')
print("Saved r19z_bifurcation_stats.png")
