import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data from the timescale gap experiment
gaps = np.array([1, 5, 10, 20, 50, 100], dtype=float)
peak_corrs = np.array([0.087, 0.271, 0.466, 0.675, 0.769, 0.800])
peak_lags = np.array([1, 3, 8, 18, 47, 97], dtype=float)

# Fit a saturation model: C(N) = C_max * (1 - exp(-N / tau))
def saturation_model(N, C_max, tau):
    return C_max * (1 - np.exp(-N / tau))

popt, pcov = curve_fit(saturation_model, gaps, peak_corrs, p0=[0.85, 20])
C_max_fit, tau_fit = popt
print(f"Saturation fit: C_max = {C_max_fit:.4f}, tau = {tau_fit:.2f}")

# Also fit lag: L(N) = a * N^b (power law)
def power_law(N, a, b):
    return a * N**b

popt_lag, _ = curve_fit(power_law, gaps[1:], peak_lags[1:], p0=[1, 1])
a_lag, b_lag = popt_lag
print(f"Lag power law: a = {a_lag:.3f}, b = {b_lag:.3f}")

# Create the definitive plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Dark theme
fig.patch.set_facecolor('#0a0a1a')
for ax in [ax1, ax2]:
    ax.set_facecolor('#0e0e1e')
    ax.tick_params(colors='#88aacc')
    ax.xaxis.label.set_color('#aaccff')
    ax.yaxis.label.set_color('#aaccff')
    ax.title.set_color('#66ddff')
    for spine in ax.spines.values():
        spine.set_color('#336')

# Plot 1: Resonance strength vs timescale gap with fit
N_fit = np.logspace(0, 2.5, 500)
C_fit = saturation_model(N_fit, C_max_fit, tau_fit)

ax1.plot(gaps, peak_corrs, 'o', color='#00ffcc', markersize=14, zorder=5, 
         markeredgecolor='#ffffff', markeredgewidth=1.5)
ax1.plot(N_fit, C_fit, '--', color='#ff6688', linewidth=2.5, alpha=0.8,
         label=f'Fit: C(N) = {C_max_fit:.3f}(1 - exp(-N/{tau_fit:.1f}))')
ax1.fill_between(N_fit, C_fit - 0.05, C_fit + 0.05, alpha=0.15, color='#ff6688')

# Annotations
ax1.annotate('No gap\n(weak resonance)', xy=(1, 0.087), xytext=(2, 0.25),
            fontsize=10, color='#ffaa44', ha='left',
            arrowprops=dict(arrowstyle='->', color='#ffaa44', lw=1.5))
ax1.annotate('Saturation\n(strong resonance)', xy=(100, 0.800), xytext=(40, 0.65),
            fontsize=10, color='#44ff88', ha='left',
            arrowprops=dict(arrowstyle='->', color='#44ff88', lw=1.5))
ax1.annotate(f'τ ≈ {tau_fit:.0f} steps\n(half-saturation)', xy=(tau_fit, saturation_model(tau_fit, C_max_fit, tau_fit)),
            xytext=(tau_fit*1.5, 0.35), fontsize=10, color='#ff6688',
            arrowprops=dict(arrowstyle='->', color='#ff6688', lw=1.5))

ax1.set_xlabel('Timescale Gap (N = sandpile steps per logistic step)', fontsize=13)
ax1.set_ylabel('|Peak Cross-Correlation|', fontsize=13)
ax1.set_title('The Resonance Gap Law\nResonance Strength vs Timescale Separation', 
              fontsize=14, fontweight='bold')
ax1.set_xscale('log')
ax1.set_ylim(0, 1.0)
ax1.legend(fontsize=11, loc='lower right', facecolor='#111128', edgecolor='#336', 
           labelcolor='#aaccff')
ax1.grid(True, alpha=0.15, color='#446')

# Plot 2: Feedback lag vs timescale gap
N_fit2 = np.logspace(0, 2.5, 500)
L_fit = power_law(N_fit2, a_lag, b_lag)

ax2.plot(gaps, peak_lags, 's', color='#ffaa44', markersize=14, zorder=5,
         markeredgecolor='#ffffff', markeredgewidth=1.5)
ax2.plot(N_fit2, L_fit, '--', color='#44aaff', linewidth=2.5, alpha=0.8,
         label=f'Fit: L(N) = {a_lag:.2f} · N^{b_lag:.2f}')

# Reference: L = N (identity, if lag = gap exactly)
ax2.plot(N_fit2, N_fit2, ':', color='#666666', linewidth=1, alpha=0.5, label='L = N (identity)')

ax2.set_xlabel('Timescale Gap (N)', fontsize=13)
ax2.set_ylabel('Feedback Lag (sandpile steps)', fontsize=13)
ax2.set_title('Feedback Delay vs Timescale Gap\nThe Slow System Leads', 
              fontsize=14, fontweight='bold')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.legend(fontsize=11, loc='upper left', facecolor='#111128', edgecolor='#336',
           labelcolor='#aaccff')
ax2.grid(True, alpha=0.15, color='#446')

plt.tight_layout()
fig.savefig('r19z_resonance_gap_law.png', dpi=150, bbox_inches='tight', 
            facecolor=fig.get_facecolor())
print("Saved r19z_resonance_gap_law.png")

# Print the law
print(f"\n=== THE RESONANCE GAP LAW ===")
print(f"C(N) = {C_max_fit:.3f} * (1 - exp(-N / {tau_fit:.1f}))")
print(f"  where C = cross-correlation, N = timescale ratio")
print(f"  C_max = {C_max_fit:.3f} (maximum achievable resonance)")
print(f"  tau = {tau_fit:.1f} (characteristic gap for half-saturation)")
print(f"\nLag scaling: L(N) = {a_lag:.2f} * N^{b_lag:.2f}")
print(f"  (approximately linear, meaning lag ≈ gap)")
