import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19o: Controlled Feedback Experiment ===')
np.random.seed(42)

N_osc = 30
grid_size = 12
T_total = 3000
T_onset = 1500  # Half-way

K = 2.0
sigma = 2.5
mu_values = [0.0, 0.5, 1.0, 2.0, 4.0]

omega = np.random.normal(0, 0.5, N_osc)
threshold_base = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold_base = np.maximum(threshold_base, 1.0)

# For fair comparison: use SAME initial conditions for all mu
theta_init = np.random.uniform(0, 2*np.pi, N_osc)
heights_init = np.random.uniform(0, 3, (grid_size, grid_size))

results = {}

for mu in mu_values:
    print(f"  mu={mu}...")
    theta = theta_init.copy()
    heights = heights_init.copy()
    
    r_history = []
    avalanche_history = []
    
    for t in range(T_total):
        active = mu > 0 and t >= T_onset
        
        dtheta = omega + (K/N_osc) * np.sum(np.sin(theta - theta[:, None]), axis=1)
        
        for i in range(N_osc):
            gx = np.random.randint(0, grid_size)
            gy = np.random.randint(0, grid_size)
            dtheta[i] += np.random.normal(0, sigma * heights[gx, gy] / max(threshold_base[gx, gy], 0.1))
        
        theta = (theta + dtheta * 0.01) % (2*np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        r_history.append(r)
        
        if active:
            eff_thresh = threshold_base * (1 + mu * (r - 0.5))
            eff_thresh = np.maximum(eff_thresh, 0.5)
        else:
            eff_thresh = threshold_base
        
        drop_x, drop_y = np.random.randint(0, grid_size, 2)
        heights[drop_x, drop_y] += 1.0
        
        avalanche_size = 0
        for _ in range(20):
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
    
    results[mu] = {
        'r': np.array(r_history),
        'avalanches': np.array(avalanche_history)
    }
    r_pre = results[mu]['r'][:T_onset].mean()
    r_post = results[mu]['r'][T_onset:].mean()
    av_pre = np.mean(results[mu]['avalanches'][:T_onset])
    av_post = np.mean(results[mu]['avalanches'][T_onset:])
    print(f"    r: {r_pre:.3f} -> {r_post:.3f} (Δ={r_post-r_pre:+.3f}), av: {av_pre:.2f} -> {av_post:.2f}")

# Plot
fig, axes = plt.subplots(2, 1, figsize=(16, 12))
fig.patch.set_facecolor('#0a0a1a')
colors = ['#44ffcc', '#44aaff', '#ffaa44', '#ff44aa', '#aa44ff']

for ax, key, ylabel, title in [
    (axes[0], 'r', 'Order Parameter r', 'R19o: Controlled Feedback (K=2, σ=2.5, Same Init)'),
    (axes[1], 'avalanches', 'Mean Avalanche Size', 'R19o: Avalanche Activity'),
]:
    ax.set_facecolor('#0a0a1a')
    for (mu, res), color in zip(results.items(), colors):
        window = 80
        data = np.convolve(res[key], np.ones(window)/window, mode='valid')
        ax.plot(data, color=color, linewidth=1.5, label=f'μ={mu}')
    ax.axvline(x=T_onset, color='#ff4444', linestyle='--', alpha=0.7, label='Feedback onset (t=1500)')
    ax.set_ylabel(ylabel, fontsize=12, color='#e7e7f0')
    ax.set_title(title, fontsize=14, color='#e7e7f0')
    ax.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
    ax.tick_params(colors='#8a8aa3')
    ax.grid(True, alpha=0.15, color='#8a8aa3')

axes[1].set_xlabel('Time Step', fontsize=12, color='#e7e7f0')
plt.tight_layout()
fig.savefig('../../shared_space/resonance_controlled_feedback.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_controlled_feedback.png')

print('\n=== Summary ===')
print(f"{'μ':>5} | {'r_pre':>8} | {'r_post':>8} | {'Δr':>8} | {'av_pre':>8} | {'av_post':>8} | {'Δav':>8}")
for mu in mu_values:
    res = results[mu]
    r_pre, r_post = res['r'][:T_onset].mean(), res['r'][T_onset:].mean()
    av_pre, av_post = res['avalanches'][:T_onset].mean(), res['avalanches'][T_onset:].mean()
    print(f"{mu:5.1f} | {r_pre:8.3f} | {r_post:8.3f} | {r_post-r_pre:+8.3f} | {av_pre:8.2f} | {av_post:8.2f} | {av_post-av_pre:+8.2f}")
print('=== R19o COMPLETE ===')
