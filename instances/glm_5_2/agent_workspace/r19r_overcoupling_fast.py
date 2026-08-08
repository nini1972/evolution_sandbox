import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19r: Over-coupling Phenomenon (Optimized) ===')
np.random.seed(42)

grid_size = 10
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

dt = 0.1
sigma_test = 3.0
T_total = 500  # Reduced for speed
N_osc = 30

omega = np.random.normal(0, 0.5, N_osc)

# Coarser K range
K_test_values = np.arange(0.5, 35, 1.0)
r_curve = []

# Precompute sin difference matrix is not possible since theta changes
# But we can vectorize the sandpile relaxation

print(f"Scanning {len(K_test_values)} K values...")

for K in K_test_values:
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    r_sum = 0
    r_count = 0
    
    for t in range(T_total):
        # Vectorized Kuramoto coupling
        sin_diff = np.sin(theta - theta[:, None])
        dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
        
        # Perturbation (vectorized random site selection)
        gx = np.random.randint(0, grid_size, N_osc)
        gy = np.random.randint(0, grid_size, N_osc)
        h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
        dtheta += np.random.normal(0, sigma_test) * h_ratio
        
        theta = (theta + dtheta * dt) % (2*np.pi)
        
        if t > 200:
            r = np.abs(np.mean(np.exp(1j * theta)))
            r_sum += r
            r_count += 1
        
        # Sandpile
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

# Find peak
peak_idx = np.argmax(r_curve)
K_peak = K_test_values[peak_idx]
r_peak = r_curve[peak_idx]

# Find K_c
K_c = None
for i in range(len(K_test_values)):
    if r_curve[i] >= 0.5:
        K_c = K_test_values[i]
        break

# Find K_upper
K_upper = None
for i in range(peak_idx, len(K_test_values)):
    if r_curve[i] < 0.5:
        K_upper = K_test_values[i]
        break

print(f"K_c (lower) = {K_c}")
print(f"K_peak = {K_peak} (r={r_peak:.4f})")
print(f"K_upper = {K_upper}")

# Plot
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

ax.plot(K_test_values, r_curve, '#44ffcc', linewidth=2.5, marker='o', markersize=3)
ax.fill_between(K_test_values, 0, r_curve, where=(r_curve >= 0.5), color='#44ffcc', alpha=0.15)

if K_c:
    ax.axvline(x=K_c, color='#ff4444', linestyle='--', alpha=0.6, label=f'K_c = {K_c:.1f}')
ax.axvline(x=K_peak, color='#ffaa44', linestyle='--', alpha=0.6, label=f'K_peak = {K_peak:.1f} (r={r_peak:.3f})')
if K_upper:
    ax.axvline(x=K_upper, color='#ff44aa', linestyle='--', alpha=0.6, label=f'K_upper = {K_upper:.1f}')

ax.axhline(y=0.5, color='#ffffff', linestyle=':', alpha=0.3)

if K_c and K_upper:
    ax.annotate('Synchronized\nWindow', xy=((K_c + K_upper)/2, 0.75), fontsize=13, 
                ha='center', color='#44ffcc', fontweight='bold')
    ax.annotate('Under-\ncoupled', xy=(K_c/2 if K_c > 1 else 0.7, 0.25), fontsize=11, 
                ha='center', color='#ff4444')
    ax.annotate('Over-\ncoupled', xy=((K_upper + K_test_values[-1])/2, 0.25), fontsize=11, 
                ha='center', color='#ff44aa')

ax.set_xlabel('Coupling K', fontsize=14, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=14, color='#e7e7f0')
ax.set_title(f'R19r: Over-coupling Phenomenon (N={N_osc}, σ={sigma_test}, dt={dt})\nNon-monotonic Synchronization Window', 
             fontsize=15, color='#e7e7f0')
ax.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0', loc='upper right')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.15, color='#8a8aa3')
ax.set_xlim(K_test_values[0], K_test_values[-1])
ax.set_ylim(0, 1.05)

plt.tight_layout()
fig.savefig('../../shared_space/resonance_overcoupling.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print(f'\nSaved: resonance_overcoupling.png')
print(f'=== R19r COMPLETE ===')
