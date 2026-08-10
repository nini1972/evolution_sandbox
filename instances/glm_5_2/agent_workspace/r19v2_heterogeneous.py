import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19v2: Heterogeneous Frequencies (Optimized) ===')
np.random.seed(42)

grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

dt = 0.1
N_osc = 20
T_sim = 800

freq_distributions = {
    'Normal N(0,0.5)': np.random.normal(0, 0.5, N_osc),
    'Bimodal ±1.5': np.concatenate([np.random.normal(-1.5, 0.3, N_osc//2), np.random.normal(1.5, 0.3, N_osc//2)]),
    'Uniform [-1,1]': np.random.uniform(-1, 1, N_osc),
}

K_values = np.arange(1, 40, 2.0)
sigma_values = [1.0, 5.0, 10.0]

fig, axes = plt.subplots(3, 3, figsize=(18, 15))
fig.patch.set_facecolor('#0a0a1a')

for col, (freq_name, omega) in enumerate(freq_distributions.items()):
    print(f"  Testing: {freq_name}")
    
    for row, sigma in enumerate(sigma_values):
        r_values = []
        
        for K in K_values:
            theta = np.random.uniform(0, 2*np.pi, N_osc)
            heights = np.random.uniform(0, 3, (grid_size, grid_size))
            
            r_sum = 0
            r_count = 0
            
            for t in range(T_sim):
                sin_diff = np.sin(theta - theta[:, None])
                dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
                
                gx = np.random.randint(0, grid_size, N_osc)
                gy = np.random.randint(0, grid_size, N_osc)
                h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
                dtheta += np.random.normal(0, sigma) * h_ratio
                
                theta = (theta + dtheta * dt) % (2*np.pi)
                
                if t > 500:
                    r = np.abs(np.mean(np.exp(1j * theta)))
                    r_sum += r
                    r_count += 1
                
                drop_x, drop_y = np.random.randint(0, grid_size, 2)
                heights[drop_x, drop_y] += 1.0
                
                for _ in range(8):
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
        
        r_values = np.array(r_values)
        
        ax = axes[col, row]
        ax.set_facecolor('#0a0a1a')
        ax.plot(K_values, r_values, '#44ffcc', linewidth=2, marker='o', markersize=3)
        
        peak_idx = np.argmax(r_values)
        peak_k = K_values[peak_idx]
        peak_r = r_values[peak_idx]
        ax.axvline(x=peak_k, color='#ff44aa', linestyle='--', alpha=0.5)
        ax.plot(peak_k, peak_r, '*', markersize=15, color='#ff44aa')
        
        decline = peak_r - r_values[-1]
        
        ax.set_title(f'{freq_name}\nσ={sigma} | K*={peak_k:.0f}, r*={peak_r:.2f}, Δ={decline:.2f}', 
                     fontsize=10, color='#e7e7f0')
        ax.set_xlabel('K', fontsize=10, color='#e7e7f0')
        ax.set_ylabel('r', fontsize=10, color='#e7e7f0')
        ax.tick_params(colors='#8a8aa3')
        ax.grid(True, alpha=0.15, color='#8a8aa3')
        ax.set_ylim(0, 1.05)
        
        print(f"    σ={sigma}: K*={peak_k:.0f}, r_max={peak_r:.3f}, decline={decline:.3f}")

fig.suptitle('R19v: Frequency Distribution Effect on Over-coupling Phenomenon', 
             fontsize=15, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_hetero_freq.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_hetero_freq.png')
print('=== R19v2 COMPLETE ===')
