import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19t: Hysteresis Test ===')
np.random.seed(42)

grid_size = 10
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

dt = 0.1
sigma_test = 5.0
N_osc = 30
omega = np.random.normal(0, 0.5, N_osc)

# Sweep K up and down, measuring r at each step
# Key: carry state forward (don't reinitialize) to test path dependence
K_sweep_up = np.arange(0.5, 40, 1.0)
K_sweep_down = np.arange(39.5, 0.5, -1.0)

T_per_step = 150  # Steps per K value

def run_sweep(K_values, initial_theta=None, initial_heights=None):
    if initial_theta is not None:
        theta = initial_theta.copy()
    else:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
    
    if initial_heights is not None:
        heights = initial_heights.copy()
    else:
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
    
    r_values = []
    
    for K in K_values:
        r_sum = 0
        r_count = 0
        
        for t in range(T_per_step):
            sin_diff = np.sin(theta - theta[:, None])
            dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
            
            gx = np.random.randint(0, grid_size, N_osc)
            gy = np.random.randint(0, grid_size, N_osc)
            h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
            dtheta += np.random.normal(0, sigma_test) * h_ratio
            
            theta = (theta + dtheta * dt) % (2*np.pi)
            
            if t > 50:
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
        
        r_values.append(r_sum / r_count)
    
    return np.array(r_values), theta, heights

print("Sweeping K up...")
r_up, theta_final_up, heights_final_up = run_sweep(K_sweep_up)

print("Sweeping K down (from final up state)...")
r_down, _, _ = run_sweep(K_sweep_down, theta_final_up, heights_final_up)

print("Sweeping K up again (from final down state)...")
K_sweep_up2 = np.arange(0.5, 40, 1.0)

# For a fresh down sweep starting from random
theta_fresh = np.random.uniform(0, 2*np.pi, N_osc)
heights_fresh = np.random.uniform(0, 3, (grid_size, grid_size))
print("Sweeping K down (fresh start from high K)...")
r_down_fresh, _, _ = run_sweep(np.arange(39.5, 0.5, -1.0), theta_fresh, heights_fresh)

# Plot
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

ax.plot(K_sweep_up, r_up, '#44ffcc', linewidth=2.5, marker='o', markersize=4, label='K swept UP (from low K)')
ax.plot(K_sweep_down, r_down, '#ff44aa', linewidth=2.5, marker='s', markersize=4, label='K swept DOWN (from high K, continued)')
ax.plot(np.arange(39.5, 0.5, -1.0), r_down_fresh, '#ffaa44', linewidth=2, marker='^', markersize=4, 
        linestyle='--', label='K swept DOWN (fresh start)')

ax.axhline(y=0.5, color='#ffffff', linestyle=':', alpha=0.3)
ax.set_xlabel('Coupling K', fontsize=14, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=14, color='#e7e7f0')
ax.set_title(f'R19t: Hysteresis Test (σ={sigma_test}, N={N_osc})\nPath Dependence in Synchronization', 
             fontsize=15, color='#e7e7f0')
ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.15, color='#8a8aa3')
ax.set_xlim(0, 40)
ax.set_ylim(0, 1.05)

# Compute hysteresis area
min_len = min(len(r_up), len(r_down))
hysteresis = np.mean(np.abs(r_up[:min_len] - r_down[::-1][:min_len]))
print(f"\nMean |Δr| (up vs down): {hysteresis:.4f}")
ax.text(20, 0.15, f'Mean |Δr| = {hysteresis:.4f}', fontsize=14, color='#ff44aa', 
        ha='center', bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#ff44aa'))

plt.tight_layout()
fig.savefig('../../shared_space/resonance_hysteresis.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print(f'\nSaved: resonance_hysteresis.png')
print('=== R19t COMPLETE ===')
