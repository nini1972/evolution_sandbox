import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from time import time

print('=== R19q: System Size Scaling ===')
np.random.seed(42)

grid_size = 10  # Smaller grid for speed
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

# Test different oscillator counts
N_values = [10, 20, 40, 60]
sigma_test = 2.0
T_total = 1500

results = {}

for N_osc in N_values:
    print(f"\n  N_osc={N_osc}...")
    omega = np.random.normal(0, 0.5, N_osc)
    
    # Test range of K values to find K_c
    K_test_values = np.arange(2, 25, 2.0)
    K_c_found = None
    
    for K in K_test_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        r_sum = 0
        r_count = 0
        
        for t in range(T_total):
            # Kuramoto (vectorized)
            dtheta = omega + (K/N_osc) * np.sum(np.sin(theta - theta[:, None]), axis=1)
            
            # Perturbation
            for i in range(N_osc):
                gx = np.random.randint(0, grid_size)
                gy = np.random.randint(0, grid_size)
                dtheta[i] += np.random.normal(0, sigma_test * heights[gx, gy] / max(threshold[gx, gy], 0.1))
            
            theta = (theta + dtheta * 0.01) % (2*np.pi)
            
            if t > 500:  # Skip transient
                r = np.abs(np.mean(np.exp(1j * theta)))
                r_sum += r
                r_count += 1
            
            # Sandpile
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
        print(f"    K={K:.1f}: r={r_mean:.3f}", end="")
        if r_mean >= 0.5 and K_c_found is None:
            K_c_found = K
            print(f" <-- K_c found!")
        else:
            print()
    
    if K_c_found is None:
        K_c_found = K_test_values[-1]
    
    results[N_osc] = {'K_c': K_c_found, 'sigma': sigma_test}
    print(f"  N={N_osc}: K_c ≈ {K_c_found:.1f}")

# Plot
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

N_arr = np.array(list(results.keys()))
K_c_arr = np.array([results[n]['K_c'] for n in N_arr])

ax.scatter(N_arr, K_c_arr, color='#44ffcc', s=150, zorder=5, edgecolors='#ffffff', linewidths=1)

# Fit: K_c = a * N^b
log_N = np.log(N_arr)
log_K = np.log(K_c_arr)
coeffs = np.polyfit(log_N, log_K, 1)
b_exp = coeffs[0]
a_coeff = np.exp(coeffs[1])

N_fine = np.linspace(5, 80, 100)
ax.plot(N_fine, a_coeff * N_fine**b_exp, '#ff44cc', linewidth=2, 
        label=f'K_c = {a_coeff:.2f} × N^{b_exp:.2f}')

ax.set_xlabel('Number of Oscillators N', fontsize=13, color='#e7e7f0')
ax.set_ylabel('Critical Coupling K_c (σ=2.0)', fontsize=13, color='#e7e7f0')
ax.set_title('R19q: Resilience Ceiling vs System Size', fontsize=14, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax.grid(True, alpha=0.2, color='#8a8aa3')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_system_size.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print(f'\nSaved: resonance_system_size.png')
print(f'Fit: K_c = {a_coeff:.2f} × N^{b_exp:.2f}')
print('=== R19q COMPLETE ===')
