import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19l: Bidirectional Coupling Experiment ===')

np.random.seed(42)

# === Parameters ===
N_osc = 30
grid_size = 12
T_total = 3000
T_onset = 1000  # When bidirectional coupling activates
K = 8.0
sigma = 1.5  # Perturbation from sandpile to oscillators
mu = 0.0    # Feedback from oscillators to sandpile (0=unidirectional, >0=bidirectional)
mu_values = [0.0, 0.1, 0.3, 0.5, 1.0, 2.0]

omega = np.random.normal(0, 0.5, N_osc)
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)

results = {}

for mu in mu_values:
    print(f"Running mu={mu}...")
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    
    r_history = []
    avalanche_history = []
    height_mean_history = []
    
    for t in range(T_total):
        active = mu > 0 and t >= T_onset
        
        # Kuramoto step
        coupling_factor = K / N_osc if not active else K / N_osc
        dtheta = omega.copy()
        for i in range(N_osc):
            for j in range(N_osc):
                dtheta[i] += (K/N_osc) * np.sin(theta[j] - theta[i])
        
        # Sandpile perturbation
        for i in range(N_osc):
            gx = np.random.randint(0, grid_size)
            gy = np.random.randint(0, grid_size)
            kick = np.random.normal(0, sigma * heights[gx, gy] / threshold[gx, gy])
            dtheta[i] += kick
        
        theta = (theta + dtheta * 0.01) % (2*np.pi)
        
        # Order parameter
        r = np.abs(np.mean(np.exp(1j * theta)))
        r_history.append(r)
        
        # Bidirectional feedback: oscillator coherence affects sandpile threshold
        if active:
            # When oscillators are coherent (high r), thresholds increase (stabilizing sandpile)
            # When incoherent (low r), thresholds decrease (destabilizing sandpile)
            threshold_mod = mu * (r - 0.5)
            effective_threshold = threshold * (1 + threshold_mod)
            effective_threshold = np.maximum(effective_threshold, 0.5)
        else:
            effective_threshold = threshold
        
        # Sandpile drive
        drop_x, drop_y = np.random.randint(0, grid_size, 2)
        heights[drop_x, drop_y] += 1.0
        
        # Toppling
        avalanche_size = 0
        toppled = True
        while toppled:
            toppled = False
            unstable = heights >= effective_threshold
            if unstable.any():
                toppled = True
                avalanche_size += unstable.sum()
                for x in range(grid_size):
                    for y in range(grid_size):
                        if heights[x, y] >= effective_threshold[x, y]:
                            heights[x, y] -= effective_threshold[x, y]
                            neighbors = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                            for nx, ny in neighbors:
                                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                                    heights[nx, ny] += effective_threshold[x, y] / 4.0
        
        avalanche_history.append(avalanche_size)
        height_mean_history.append(heights.mean())
    
    results[mu] = {
        'r': np.array(r_history),
        'avalanches': np.array(avalanche_history),
        'heights': np.array(height_mean_history)
    }

# === Plotting ===
fig, axes = plt.subplots(3, 1, figsize=(16, 18))
fig.patch.set_facecolor('#0a0a1a')
colors = ['#44ffcc', '#44aaff', '#ffaa44', '#ff44aa', '#aa44ff', '#44ffaa']

# Plot 1: Order parameter
ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
for (mu, res), color in zip(results.items(), colors):
    # Smooth with moving average
    window = 50
    r_smooth = np.convolve(res['r'], np.ones(window)/window, mode='valid')
    ax1.plot(r_smooth, color=color, linewidth=1.5, label=f'μ={mu}')
ax1.axvline(x=T_onset, color='#ff4444', linestyle='--', alpha=0.7, label='Coupling onset')
ax1.set_ylabel('Order Parameter r', fontsize=12, color='#e7e7f0')
ax1.set_title('R19l: Oscillator Synchronization (Bidirectional Coupling)', fontsize=14, color='#e7e7f0')
ax1.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15, color='#8a8aa3')

# Plot 2: Avalanche sizes
ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
for (mu, res), color in zip(results.items(), colors):
    window = 50
    av_smooth = np.convolve(res['avalanches'], np.ones(window)/window, mode='valid')
    ax2.plot(av_smooth, color=color, linewidth=1.5, label=f'μ={mu}')
ax2.axvline(x=T_onset, color='#ff4444', linestyle='--', alpha=0.7)
ax2.set_ylabel('Mean Avalanche Size', fontsize=12, color='#e7e7f0')
ax2.set_title('R19l: Sandpile Avalanche Activity', fontsize=14, color='#e7e7f0')
ax2.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.15, color='#8a8aa3')

# Plot 3: Mean height
ax3 = axes[2]
ax3.set_facecolor('#0a0a1a')
for (mu, res), color in zip(results.items(), colors):
    window = 50
    h_smooth = np.convolve(res['heights'], np.ones(window)/window, mode='valid')
    ax3.plot(h_smooth, color=color, linewidth=1.5, label=f'μ={mu}')
ax3.axvline(x=T_onset, color='#ff4444', linestyle='--', alpha=0.7)
ax3.set_ylabel('Mean Sandpile Height', fontsize=12, color='#e7e7f0')
ax3.set_xlabel('Time Step', fontsize=12, color='#e7e7f0')
ax3.set_title('R19l: Sandpile Energy Level', fontsize=14, color='#e7e7f0')
ax3.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax3.tick_params(colors='#8a8aa3')
ax3.grid(True, alpha=0.15, color='#8a8aa3')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_bidirectional.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_bidirectional.png')

# Summary statistics
print('\n=== Summary (post-onset, t > 1000) ===')
for mu in mu_values:
    res = results[mu]
    r_post = res['r'][T_onset:].mean()
    av_post = res['avalanches'][T_onset:].mean()
    h_post = res['heights'][T_onset:].mean()
    print(f"mu={mu}: r={r_post:.3f}, av_size={av_post:.2f}, mean_height={h_post:.3f}")

print('=== R19l COMPLETE ===')
