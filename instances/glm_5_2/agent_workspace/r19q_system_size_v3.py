import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19q v3: System Size Scaling ===')
np.random.seed(42)

grid_size = 10
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

# Scale perturbation properly: use sigma=10 so the kicks are significant
sigma_test = 10.0
T_total = 800
N_values = [10, 20, 40, 60]

results = {}

for N_osc in N_values:
    print(f"  N_osc={N_osc}...")
    omega = np.random.normal(0, 0.5, N_osc)
    
    K_test_values = np.arange(1, 35, 2.0)
    K_c_found = None
    r_curve = []
    
    for K in K_test_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        r_sum = 0
        r_count = 0
        
        for t in range(T_total):
            dtheta = omega + (K/N_osc) * np.sum(np.sin(theta - theta[:, None]), axis=1)
            
            for i in range(N_osc):
                gx = np.random.randint(0, grid_size)
                gy = np.random.randint(0, grid_size)
                dtheta[i] += np.random.normal(0, sigma_test * heights[gx, gy] / max(threshold[gx, gy], 0.1))
            
            theta = (theta + dtheta * 0.01) % (2*np.pi)
            
            if t > 300:
                r = np.abs(np.mean(np.exp(1j * theta)))
                r_sum += r
                r_count += 1
            
            drop_x, drop_y = np.random.randint(0, grid_size, 2)
            heights[drop_x, drop_y] += 1.0
            
            for _ in range(15):
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
        
        if r_mean >= 0.5 and K_c_found is None:
            K_c_found = K
    
    if K_c_found is None:
        K_c_found = K_test_values[-1]
    
    results[N_osc] = {'K_c': K_c_found, 'K_values': K_test_values, 'r_curve': np.array(r_curve)}
    print(f"    K_c ≈ {K_c_found:.1f}, max_r={max(r_curve):.3f}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.patch.set_facecolor('#0a0a1a')
colors = ['#44ffcc', '#44aaff', '#ffaa44', '#ff44aa']

ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
for (N, res), color in zip(results.items(), colors):
    ax1.plot(res['K_values'], res['r_curve'], color=color, linewidth=2, marker='o', markersize=3, label=f'N={N}')
ax1.axhline(y=0.5, color='#ff4444', linestyle='--', alpha=0.5, label='r=0.5')
ax1.set_xlabel('Coupling K', fontsize=12, color='#e7e7f0')
ax1.set_ylabel('Order Parameter r', fontsize=12, color='#e7e7f0')
ax1.set_title(f'Sync Transition (σ={sigma_test})', fontsize=14, color='#e7e7f0')
ax1.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15, color='#8a8aa3')

ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
N_arr = np.array(list(results.keys()))
K_c_arr = np.array([results[n]['K_c'] for n in N_arr])
ax2.scatter(N_arr, K_c_arr, color='#44ffcc', s=150, zorder=5, edgecolors='#ffffff', linewidths=1)

if len(N_arr) >= 2:
    log_N = np.log(N_arr)
    log_K = np.log(K_c_arr)
    coeffs = np.polyfit(log_N, log_K, 1)
    b_exp = coeffs[0]
    a_coeff = np.exp(coeffs[1])
    N_fine = np.linspace(5, 80, 100)
    ax2.plot(N_fine, a_coeff * N_fine**b_exp, '#ff44cc', linewidth=2, 
             label=f'K_c ≈ {a_coeff:.2f} × N^{b_exp:.2f}')
    ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')

ax2.set_xlabel('Number of Oscillators N', fontsize=12, color='#e7e7f0')
ax2.set_ylabel('Critical Coupling K_c', fontsize=12, color='#e7e7f0')
ax2.set_title('Resilience Ceiling vs System Size', fontsize=14, color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#8a8aa3')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_system_size.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print(f'\nK_c values: {dict(zip(N_arr, K_c_arr))}')
if len(N_arr) >= 2:
    print(f'Power law fit: K_c ≈ {a_coeff:.2f} × N^{b_exp:.2f}')
print('=== R19q COMPLETE ===')
