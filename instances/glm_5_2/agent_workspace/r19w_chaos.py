import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19w: Chaos at the Transition Boundary ===')
np.random.seed(42)

grid_size = 6
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
dt = 0.1
N_osc = 15
T_sim = 1000

sigma_values = [1.0, 5.0, 10.0]
K_values = np.arange(1, 25, 1.0)

fig, axes = plt.subplots(2, 1, figsize=(16, 12))
fig.patch.set_facecolor('#0a0a1a')

ax_r = axes[0]
ax_var = axes[1]
ax_r.set_facecolor('#0a0a1a')
ax_var.set_facecolor('#0a0a1a')

colors = ['#44ffcc', '#ff44aa', '#ffaa44']

for si, sigma in enumerate(sigma_values):
    print(f"  sigma = {sigma}")
    r_means = []
    r_stds = []
    r_maxs = []
    r_mins = []
    
    for K in K_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        
        r_history = []
        
        for t in range(T_sim):
            sin_diff = np.sin(theta - theta[:, None])
            dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
            
            gx = np.random.randint(0, grid_size, N_osc)
            gy = np.random.randint(0, grid_size, N_osc)
            h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
            dtheta += np.random.normal(0, sigma) * h_ratio
            
            theta = (theta + dtheta * dt) % (2*np.pi)
            
            if t > 300:
                r = np.abs(np.mean(np.exp(1j * theta)))
                r_history.append(r)
            
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
        
        r_history = np.array(r_history)
        r_means.append(np.mean(r_history))
        r_stds.append(np.std(r_history))
        r_maxs.append(np.max(r_history))
        r_mins.append(np.min(r_history))
    
    r_means = np.array(r_means)
    r_stds = np.array(r_stds)
    r_maxs = np.array(r_maxs)
    r_mins = np.array(r_mins)
    
    label = f'sigma={sigma}'
    ax_r.plot(K_values, r_means, color=colors[si], linewidth=2, label=label)
    ax_r.fill_between(K_values, r_mins, r_maxs, alpha=0.15, color=colors[si])
    ax_var.plot(K_values, r_stds, color=colors[si], linewidth=2, label=label)
    
    peak_var_idx = np.argmax(r_stds)
    peak_k = K_values[peak_var_idx]
    print(f"    Peak variability at K={peak_k:.1f}, std={r_stds[peak_var_idx]:.4f}, r={r_means[peak_var_idx]:.3f}")
    
    # Also report the K with maximum std in the synchronized region (K > 5)
    high_k_mask = K_values > 5
    if high_k_mask.any():
        high_k_stds = r_stds[high_k_mask]
        high_k_vals = K_values[high_k_mask]
        peak_hk_idx = np.argmax(high_k_stds)
        print(f"    Peak variability (K>5) at K={high_k_vals[peak_hk_idx]:.1f}, std={high_k_stds[peak_hk_idx]:.4f}")

ax_r.set_title('Order Parameter r vs K (mean with min/max band)', fontsize=14, color='#44ffcc')
ax_r.set_xlabel('K', color='#e7e7f0')
ax_r.set_ylabel('r (mean range)', color='#e7e7f0')
ax_r.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax_r.tick_params(colors='#8a8aa3')
ax_r.grid(True, alpha=0.15, color='#8a8aa3')
ax_r.set_ylim(0, 1.05)

ax_var.set_title('Temporal Variability of r (std over time) - Chaos Indicator', fontsize=14, color='#44ffcc')
ax_var.set_xlabel('K', color='#e7e7f0')
ax_var.set_ylabel('std(r) over time', color='#e7e7f0')
ax_var.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax_var.tick_params(colors='#8a8aa3')
ax_var.grid(True, alpha=0.15, color='#8a8aa3')

fig.suptitle('R19w: Chaos at the Transition Boundary - Temporal Variability of Order Parameter', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_chaos_transition.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_chaos_transition.png')
print('=== R19w COMPLETE ===')
