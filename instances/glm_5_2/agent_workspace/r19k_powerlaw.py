import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19k: Power-Law Fit of Transition Boundary ===')

data = np.load('../../shared_space/resonance_phase_diagram_data.npz')
K_values = data['K_values']
sigma_values = data['sigma_values']
phase_grid = data['phase_grid']

# For each sigma, find the critical K where r crosses 0.5
critical_K = []
valid_sigmas = []

for si, sigma in enumerate(sigma_values):
    row = phase_grid[si, :]
    # Find first K where r >= 0.5 (going from low to high K)
    found = False
    for ki, K in enumerate(K_values):
        if row[ki] >= 0.5:
            # Linear interpolation
            if ki > 0:
                r_low = row[ki-1]
                r_high = row[ki]
                K_low = K_values[ki-1]
                K_high = K_values[ki]
                # Interpolate to find K where r = 0.5
                if r_high != r_low:
                    frac = (0.5 - r_low) / (r_high - r_low)
                    K_crit = K_low + frac * (K_high - K_low)
                else:
                    K_crit = K_high
            else:
                K_crit = K_values[0]
            critical_K.append(K_crit)
            valid_sigmas.append(sigma)
            found = True
            break
    if not found:
        print(f"  sigma={sigma:.2f}: No transition found (max r = {row.max():.3f})")

critical_K = np.array(critical_K)
valid_sigmas = np.array(valid_sigmas)

print(f"Found {len(valid_sigmas)} transition points")

# Fit power law: K_crit = A * sigma^B
# Only fit for sigma > 0.1 (sigma=0 has no perturbation)
mask = valid_sigmas > 0.1
if mask.sum() >= 3:
    log_sigma = np.log(valid_sigmas[mask])
    log_K = np.log(critical_K[mask])
    
    # Linear fit in log space: log(K) = B*log(sigma) + log(A)
    coeffs = np.polyfit(log_sigma, log_K, 1)
    B = coeffs[0]
    A = np.exp(coeffs[1])
    
    print(f"Power law fit: K_crit = {A:.2f} * sigma^{B:.2f}")
    
    # R-squared
    K_pred = A * valid_sigmas[mask]**B
    ss_res = np.sum((critical_K[mask] - K_pred)**2)
    ss_tot = np.sum((critical_K[mask] - np.mean(critical_K[mask]))**2)
    r_sq = 1 - ss_res / ss_tot
    print(f"R² = {r_sq:.4f}")
else:
    print("Not enough points for power law fit")
    A, B, r_sq = 0, 0, 0

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#0a0a1a')

# Left: raw data + fit
ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
ax1.scatter(valid_sigmas[mask], critical_K[mask], color='#44ffcc', s=100, zorder=5, edgecolors='#ffffff', linewidths=0.5)
sigma_fine = np.linspace(0.1, 5.0, 100)
ax1.plot(sigma_fine, A * sigma_fine**B, 'r--', linewidth=2, label=f'Fit: K = {A:.2f}σ^{B:.2f}')
ax1.set_xlabel('Perturbation Strength σ', fontsize=12, color='#e7e7f0')
ax1.set_ylabel('Critical Coupling K_c', fontsize=12, color='#e7e7f0')
ax1.set_title('Transition Boundary: Critical K vs σ', fontsize=13, color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax1.grid(True, alpha=0.2, color='#8a8aa3')

# Right: log-log plot
ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
ax2.scatter(np.log(valid_sigmas[mask]), np.log(critical_K[mask]), color='#44ffcc', s=100, zorder=5, edgecolors='#ffffff', linewidths=0.5)
log_sigma_fine = np.linspace(-2.3, 1.6, 100)
ax2.plot(log_sigma_fine, np.polyval(coeffs, log_sigma_fine), 'r--', linewidth=2, 
         label=f'slope = {B:.2f}')
ax2.set_xlabel('ln(σ)', fontsize=12, color='#e7e7f0')
ax2.set_ylabel('ln(K_c)', fontsize=12, color='#e7e7f0')
ax2.set_title(f'Log-Log Plot (R² = {r_sq:.3f})', fontsize=13, color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax2.grid(True, alpha=0.2, color='#8a8aa3')

fig.suptitle('R19k: Power-Law Structure of the Critical Boundary', fontsize=15, color='#e7e7f0', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_powerlaw_boundary.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_powerlaw_boundary.png')

# Save fit parameters
with open('../../shared_space/resonance_powerlaw_fit.txt', 'w') as f:
    f.write(f"Power law fit: K_crit = {A:.4f} * sigma^{B:.4f}\n")
    f.write(f"R-squared: {r_sq:.4f}\n")
    f.write(f"Data points: {mask.sum()}\n")
    for s, k in zip(valid_sigmas[mask], critical_K[mask]):
        f.write(f"  sigma={s:.4f}, K_crit={k:.4f}\n")
print('Saved: resonance_powerlaw_fit.txt')
print('=== R19k Power Law COMPLETE ===')
