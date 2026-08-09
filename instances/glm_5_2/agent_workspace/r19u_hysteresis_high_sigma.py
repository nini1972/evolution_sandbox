import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19u: Hysteresis at Higher Sigma ===')
np.random.seed(42)

grid_size = 10
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

dt = 0.1
N_osc = 30
omega = np.random.normal(0, 0.5, N_osc)
T_per_step = 150

def run_sweep(K_values, sigma, initial_theta=None, initial_heights=None):
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
            dtheta += np.random.normal(0, sigma) * h_ratio
            
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

K_up = np.arange(0.5, 40, 1.0)
K_down = np.arange(39.5, 0.5, -1.0)

sigma_values = [3.0, 5.0, 8.0]
hysteresis_values = {}

fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.patch.set_facecolor('#0a0a1a')
colors = ['#44ffcc', '#ffaa44', '#ff44aa']

for idx, (sigma, color) in enumerate(zip(sigma_values, colors)):
    print(f"  σ={sigma}...")
    
    r_up, theta_f, heights_f = run_sweep(K_up, sigma)
    r_down, _, _ = run_sweep(K_down, sigma, theta_f, heights_f)
    
    min_len = min(len(r_up), len(r_down))
    hyst = np.mean(np.abs(r_up[:min_len] - r_down[::-1][:min_len]))
    hysteresis_values[sigma] = hyst
    print(f"    Hysteresis: {hyst:.4f}")
    
    ax = axes[idx]
    ax.set_facecolor('#0a0a1a')
    ax.plot(K_up, r_up, '#44ffcc', linewidth=2, marker='o', markersize=3, label='K up')
    ax.plot(K_down, r_down, '#ff44aa', linewidth=2, marker='s', markersize=3, label='K down')
    ax.set_title(f'σ={sigma}\nHysteresis = {hyst:.4f}', fontsize=13, color='#e7e7f0')
    ax.set_xlabel('K', fontsize=11, color='#e7e7f0')
    ax.set_ylabel('r', fontsize=11, color='#e7e7f0')
    ax.legend(fontsize=10, facecolor='#1a1a2e', edgecolor=color, labelcolor='#e7e7f0')
    ax.tick_params(colors='#8a8aa3')
    ax.grid(True, alpha=0.15, color='#8a8aa3')
    ax.set_ylim(0, 1.05)

fig.suptitle('R19u: Hysteresis Analysis — Path Independence Test', fontsize=16, color='#44ffcc', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_hysteresis_multi.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')

print(f'\nHysteresis values: {hysteresis_values}')
print('Small hysteresis → smooth crossover (not first-order transition)')
print('=== R19u COMPLETE ===')
