import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19s: Over-coupling at Multiple Sigma ===')
np.random.seed(42)

grid_size = 10
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

dt = 0.1
T_total = 500
N_osc = 30
omega = np.random.normal(0, 0.5, N_osc)

sigma_values = [1.0, 3.0, 5.0, 8.0]
K_test_values = np.arange(0.5, 40, 1.0)

results = {}

for sigma in sigma_values:
    print(f"  σ={sigma}...")
    r_curve = []
    
    for K in K_test_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        r_sum = 0
        r_count = 0
        
        for t in range(T_total):
            sin_diff = np.sin(theta - theta[:, None])
            dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
            
            gx = np.random.randint(0, grid_size, N_osc)
            gy = np.random.randint(0, grid_size, N_osc)
            h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
            dtheta += np.random.normal(0, sigma) * h_ratio
            
            theta = (theta + dtheta * dt) % (2*np.pi)
            
            if t > 200:
                r = np.abs(np.mean(np.exp(1j * theta)))
                r_sum += r
                r_count += 1
            
            drop_x, drop_y = np.random.randint(0, grid_size, 2)
            heights[drop_x, drop_y] += 1.0
            
            for _ in range(10):
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
        
        r_mean = r_sum / r_count
        r_curve.append(r_mean)
    
    r_curve = np.array(r_curve)
    results[sigma] = r_curve
    
    peak_idx = np.argmax(r_curve)
    print(f"    Peak at K={K_test_values[peak_idx]:.1f} (r={r_curve[peak_idx]:.3f}), r_final={r_curve[-1]:.3f}")

# Plot
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')
colors = ['#44ffcc', '#44aaff', '#ffaa44', '#ff44aa']

for (sigma, r_curve), color in zip(results.items(), colors):
    ax.plot(K_test_values, r_curve, color=color, linewidth=2, marker='o', markersize=3, label=f'σ={sigma}')
    peak_idx = np.argmax(r_curve)
    ax.plot(K_test_values[peak_idx], r_curve[peak_idx], color=color, marker='*', markersize=15, zorder=5)

ax.axhline(y=0.5, color='#ffffff', linestyle=':', alpha=0.3, label='r=0.5')
ax.set_xlabel('Coupling K', fontsize=14, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=14, color='#e7e7f0')
ax.set_title(f'R19s: Over-coupling at Multiple σ (N={N_osc}, dt={dt})\n★ marks peak synchronization', 
             fontsize=15, color='#e7e7f0')
ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.15, color='#8a8aa3')
ax.set_xlim(K_test_values[0], K_test_values[-1])
ax.set_ylim(0, 1.05)

plt.tight_layout()
fig.savefig('../../shared_space/resonance_overcoupling_multi_sigma.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print(f'\nSaved: resonance_overcoupling_multi_sigma.png')

print('\n=== Summary ===')
for sigma, r_curve in results.items():
    peak_idx = np.argmax(r_curve)
    K_peak = K_test_values[peak_idx]
    r_peak = r_curve[peak_idx]
    r_low_K = r_curve[0]
    r_high_K = r_curve[-1]
    print(f"σ={sigma}: peak K={K_peak:.1f} (r={r_peak:.3f}), r(K=0.5)={r_low_K:.3f}, r(K=39.5)={r_high_K:.3f}, decline={r_peak-r_high_K:.3f}")
print('=== R19s COMPLETE ===')
