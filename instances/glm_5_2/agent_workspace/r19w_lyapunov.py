import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19w2: Lyapunov Exponent Measurement ===')
np.random.seed(42)

grid_size = 6
threshold_base = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold_base = np.maximum(threshold_base, 1.0)
dt = 0.1
N_osc = 15
T_sim = 600
T_lyap = 300  # steps to measure divergence

sigma = 5.0  # Use moderate sigma where transition is interesting
K_values = np.arange(1, 25, 0.5)
epsilon = 1e-4  # initial perturbation

lyap_exponents = []
r_means = []

for K in K_values:
    # Run two trajectories with tiny initial difference
    theta1 = np.random.uniform(0, 2*np.pi, N_osc)
    theta2 = theta1 + np.random.normal(0, epsilon, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    
    r_history = []
    divergences = []
    
    for t in range(T_sim):
        # Trajectory 1
        sin_diff1 = np.sin(theta1 - theta1[:, None])
        dtheta1 = omega + (K/N_osc) * sin_diff1.sum(axis=1)
        gx = np.random.randint(0, grid_size, N_osc)
        gy = np.random.randint(0, grid_size, N_osc)
        h_ratio = heights[gx, gy] / np.maximum(threshold_base[gx, gy], 0.1)
        # Use same random perturbation for both (to isolate deterministic divergence)
        kicks = np.random.normal(0, sigma) * h_ratio
        dtheta1 += kicks
        theta1 = (theta1 + dtheta1 * dt) % (2*np.pi)
        
        # Trajectory 2 (same kicks)
        sin_diff2 = np.sin(theta2 - theta2[:, None])
        dtheta2 = omega + (K/N_osc) * sin_diff2.sum(axis=1)
        dtheta2 += kicks  # same perturbation
        theta2 = (theta2 + dtheta2 * dt) % (2*np.pi)
        
        if t > 200:
            r = np.abs(np.mean(np.exp(1j * theta1)))
            r_history.append(r)
            
            if t > 200 and t < 200 + T_lyap:
                # Measure phase difference (accounting for wrapping)
                diff = np.angle(np.exp(1j * (theta1 - theta2)))
                div = np.sqrt(np.mean(diff**2))
                divergences.append(div)
        
        # Sandpile dynamics (same for both)
        drop_x, drop_y = np.random.randint(0, grid_size, 2)
        heights[drop_x, drop_y] += 1.0
        for _ in range(6):
            unstable = heights >= threshold_base
            if not unstable.any():
                break
            for x in range(grid_size):
                for y in range(grid_size):
                    if heights[x, y] >= threshold_base[x, y]:
                        h_drop = threshold_base[x, y]
                        heights[x, y] -= h_drop
                        for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                                heights[nx, ny] += h_drop / 4.0
    
    r_means.append(np.mean(r_history))
    
    # Compute Lyapunov exponent from divergence rate
    divergences = np.array(divergences)
    # Only use first ~50 steps where divergence is still exponential (before saturation)
    n_fit = min(50, len(divergences))
    if n_fit > 5 and divergences[0] > 0:
        log_div = np.log(np.maximum(divergences[:n_fit], 1e-20))
        t_fit = np.arange(n_fit) * dt
        # Linear fit: log(div) = log(eps) + lambda * t
        coeffs = np.polyfit(t_fit, log_div, 1)
        lyap = coeffs[0]
    else:
        lyap = 0.0
    
    lyap_exponents.append(lyap)

lyap_exponents = np.array(lyap_exponents)
r_means = np.array(r_means)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(16, 12))
fig.patch.set_facecolor('#0a0a1a')

ax1 = axes[0]
ax2 = axes[1]
ax1.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')

ax1.plot(K_values, r_means, color='#44ffcc', linewidth=2.5)
ax1.set_title(f'Order Parameter r vs K (sigma={sigma})', fontsize=14, color='#44ffcc')
ax1.set_xlabel('K', color='#e7e7f0')
ax1.set_ylabel('r (mean)', color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15, color='#8a8aa3')
ax1.set_ylim(0, 1.05)

# Color the Lyapunov plot by sign
colors = ['#ff4444' if l > 0 else '#44aaff' for l in lyap_exponents]
ax2.bar(K_values, lyap_exponents, width=0.3, color=colors, alpha=0.8)
ax2.axhline(y=0, color='#e7e7f0', linewidth=1, linestyle='--')
ax2.set_title('Finite-Time Lyapunov Exponent vs K (sigma=5)', fontsize=14, color='#44ffcc')
ax2.set_xlabel('K', color='#e7e7f0')
ax2.set_ylabel('Lyapunov exponent (1/dt)', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.15, color='#8a8aa3')

# Annotate regions
peak_lyap_idx = np.argmax(lyap_exponents)
peak_k = K_values[peak_lyap_idx]
print(f"Peak Lyapunov exponent: lambda={lyap_exponents[peak_lyap_idx]:.4f} at K={peak_k:.1f}")
print(f"r at peak: {r_means[peak_lyap_idx]:.3f}")

# Find where Lyapunov crosses zero
sign_changes = np.where(np.diff(np.sign(lyap_exponents)))[0]
for sc in sign_changes:
    print(f"  Sign change at K ~ {K_values[sc]:.1f} to {K_values[sc+1]:.1f}")

fig.suptitle('R19w2: Lyapunov Exponent Analysis - Chaos at Transition Boundary', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_lyapunov.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('\nSaved: resonance_lyapunov.png')
print('=== R19w2 COMPLETE ===')
