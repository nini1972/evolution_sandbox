import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19l: Bidirectional Coupling (Optimized) ===')
np.random.seed(42)

N_osc = 30
grid_size = 12
T_total = 2000
T_onset = 700
K = 8.0
sigma = 1.5
mu_values = [0.0, 0.3, 1.0, 2.0]

omega = np.random.normal(0, 0.5, N_osc)
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

results = {}

for mu in mu_values:
    print(f"  mu={mu}...")
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    
    r_history = []
    avalanche_history = []
    height_mean_history = []
    
    for t in range(T_total):
        active = mu > 0 and t >= T_onset
        
        # Kuramoto step (vectorized)
        dtheta = omega + (K/N_osc) * np.sum(np.sin(theta - theta[:, None]), axis=1)
        
        # Sandpile perturbation (sample from heights/threshold)
        for i in range(N_osc):
            gx = np.random.randint(0, grid_size)
            gy = np.random.randint(0, grid_size)
            dtheta[i] += np.random.normal(0, sigma * heights[gx, gy] / max(threshold[gx, gy], 0.1))
        
        theta = (theta + dtheta * 0.01) % (2*np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        r_history.append(r)
        
        # Effective threshold
        if active:
            eff_thresh = threshold * (1 + mu * (r - 0.5))
            eff_thresh = np.maximum(eff_thresh, 0.5)
        else:
            eff_thresh = threshold
        
        # Sandpile
        drop_x, drop_y = np.random.randint(0, grid_size, 2)
        heights[drop_x, drop_y] += 1.0
        
        avalanche_size = 0
        for _ in range(20):  # Max relaxation rounds
            unstable = heights >= eff_thresh
            if not unstable.any():
                break
            avalanche_size += unstable.sum()
            for x in range(grid_size):
                for y in range(grid_size):
                    if heights[x, y] >= eff_thresh[x, y]:
                        h_drop = eff_thresh[x, y]
                        heights[x, y] -= h_drop
                        for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                                heights[nx, ny] += h_drop / 4.0
        
        avalanche_history.append(avalanche_size)
        height_mean_history.append(heights.mean())
    
    results[mu] = {
        'r': np.array(r_history),
        'avalanches': np.array(avalanche_history),
        'heights': np.array(height_mean_history)
    }
    print(f"    r_mean={np.mean(r_history[T_onset:]):.3f}")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(16, 18))
fig.patch.set_facecolor('#0a0a1a')
colors = ['#44ffcc', '#ffaa44', '#ff44aa', '#aa44ff']

for ax, key, ylabel, title in [
    (axes[0], 'r', 'Order Parameter r', 'R19l: Oscillator Synchronization'),
    (axes[1], 'avalanches', 'Mean Avalanche Size', 'R19l: Sandpile Avalanche Activity'),
    (axes[2], 'heights', 'Mean Sandpile Height', 'R19l: Sandpile Energy Level'),
]:
    ax.set_facecolor('#0a0a1a')
    for (mu, res), color in zip(results.items(), colors):
        window = 50
        data = np.convolve(res[key], np.ones(window)/window, mode='valid')
        ax.plot(data, color=color, linewidth=1.5, label=f'μ={mu}')
    ax.axvline(x=T_onset, color='#ff4444', linestyle='--', alpha=0.7)
    ax.set_ylabel(ylabel, fontsize=12, color='#e7e7f0')
    ax.set_title(title, fontsize=14, color='#e7e7f0')
    ax.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
    ax.tick_params(colors='#8a8aa3')
    ax.grid(True, alpha=0.15, color='#8a8aa3')

axes[2].set_xlabel('Time Step', fontsize=12, color='#e7e7f0')
plt.tight_layout()
fig.savefig('../../shared_space/resonance_bidirectional.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_bidirectional.png')

print('\n=== Summary (post-onset) ===')
for mu in mu_values:
    res = results[mu]
    print(f"mu={mu}: r={res['r'][T_onset:].mean():.3f}, av={res['avalanches'][T_onset:].mean():.2f}, h={res['heights'][T_onset:].mean():.3f}")
print('=== R19l COMPLETE ===')
