import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

print('=== R19k: Saturating Boundary Fit ===')

data = np.load('../../shared_space/resonance_phase_diagram_data.npz')
K_values = data['K_values']
sigma_values = data['sigma_values']
phase_grid = data['phase_grid']

# Extract critical K for r=0.5 boundary
critical_K = []
valid_sigmas = []

for si, sigma in enumerate(sigma_values):
    row = phase_grid[si, :]
    found = False
    for ki, K in enumerate(K_values):
        if row[ki] >= 0.5:
            if ki > 0:
                r_low, r_high = row[ki-1], row[ki]
                K_low, K_high = K_values[ki-1], K_values[ki]
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
        print(f"  sigma={sigma:.2f}: No transition found")

critical_K = np.array(critical_K)
valid_sigmas = np.array(valid_sigmas)

# Try saturating model: K_crit = K_max * (1 - exp(-alpha * sigma))
def saturating(sigma, K_max, alpha):
    return K_max * (1 - np.exp(-alpha * sigma))

mask = valid_sigmas > 0.1
sigma_fit = valid_sigmas[mask]
K_fit = critical_K[mask]

try:
    popt, pcov = curve_fit(saturating, sigma_fit, K_fit, p0=[20, 0.5], maxfev=5000)
    K_max, alpha = popt
    K_pred = saturating(sigma_fit, *popt)
    ss_res = np.sum((K_fit - K_pred)**2)
    ss_tot = np.sum((K_fit - np.mean(K_fit))**2)
    r_sq = 1 - ss_res / ss_tot
    print(f"Saturating fit: K_c = {K_max:.2f} * (1 - exp(-{alpha:.3f} * sigma))")
    print(f"R² = {r_sq:.4f}")
except Exception as e:
    print(f"Fit failed: {e}")
    K_max, alpha, r_sq = 20, 0.5, 0

# Also try power law for comparison
log_sigma = np.log(sigma_fit)
log_K = np.log(K_fit)
coeffs_pl = np.polyfit(log_sigma, log_K, 1)
B_pl = coeffs_pl[0]
A_pl = np.exp(coeffs_pl[1])
K_pred_pl = A_pl * sigma_fit**B_pl
r_sq_pl = 1 - np.sum((K_fit - K_pred_pl)**2) / np.sum((K_fit - np.mean(K_fit))**2)
print(f"Power law: K = {A_pl:.2f} * sigma^{B_pl:.2f}, R² = {r_sq_pl:.4f}")

# Plot both models
fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

ax.scatter(sigma_fit, K_fit, color='#44ffcc', s=120, zorder=5, edgecolors='#ffffff', linewidths=0.8, label='Data points')

sigma_fine = np.linspace(0.01, 5.5, 200)
ax.plot(sigma_fine, saturating(sigma_fine, *popt), '#ff44cc', linewidth=2.5, 
        label=f'Saturating: K = {K_max:.1f}(1-e^{{-{alpha:.2f}σ}})  R²={r_sq:.3f}')
ax.plot(sigma_fine, A_pl * sigma_fine**B_pl, '#ffaa44', linewidth=2, linestyle='--',
        label=f'Power law: K = {A_pl:.1f}σ^{B_pl:.2f}  R²={r_sq_pl:.3f}')

ax.axhline(y=K_max, color='#ff44cc', linestyle=':', alpha=0.5, label=f'K_max = {K_max:.1f} (saturation)')

ax.set_xlabel('Perturbation Strength σ', fontsize=13, color='#e7e7f0')
ax.set_ylabel('Critical Coupling K_c (r=0.5)', fontsize=13, color='#e7e7f0')
ax.set_title('R19k: Critical Boundary — Saturating vs Power-Law Fit', fontsize=14, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.legend(fontsize=11, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax.grid(True, alpha=0.2, color='#8a8aa3')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_saturation_boundary.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_saturation_boundary.png')
print('=== COMPLETE ===')
