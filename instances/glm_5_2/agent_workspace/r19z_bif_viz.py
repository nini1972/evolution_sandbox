import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('r19z_bifurcation.json'))

ks = sorted([int(k) for k in data.keys()])
r_means = [data[str(k)]['r_mean'] for k in ks]
r_stds = [data[str(k)]['r_std'] for k in ks]
osc_strs = [data[str(k)]['osc_strength'] for k in ks]
osc_periods = [data[str(k)]['osc_period'] for k in ks]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel 1: r_mean and r_std vs K
ax = axes[0, 0]
ax2 = ax.twinx()
ax.plot(ks, r_means, 'bo-', label='r_mean', markersize=8)
ax2.plot(ks, r_stds, 'rs--', label='r_std', markersize=8)
ax.set_xlabel('Coupling K')
ax.set_ylabel('r_mean', color='blue')
ax2.set_ylabel('r_std', color='red')
ax.set_title('Order parameter vs K (α=0.9, σ=100)\nBifurcation diagram')
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, loc='center right')
ax.grid(True, alpha=0.3)

# Panel 2: Oscillation strength vs K
ax = axes[0, 1]
colors = ['red' if s > 0.15 else 'blue' for s in osc_strs]
ax.bar(range(len(ks)), osc_strs, color=colors, alpha=0.7)
ax.set_xticks(range(len(ks)))
ax.set_xticklabels(ks)
ax.set_xlabel('Coupling K')
ax.set_ylabel('Oscillation strength (autocorrelation peak)')
ax.set_title('Oscillation strength vs K\nRed = oscillating, Blue = stable')
ax.axhline(0.15, color='gray', linestyle='--', alpha=0.5, label='threshold')
ax.legend()
ax.grid(True, alpha=0.3)

# Annotate oscillation region
osc_ks = [k for k, s in zip(ks, osc_strs) if s > 0.15]
if osc_ks:
    ax.annotate(f'Oscillation region:\nK ∈ {{{", ".join(map(str, osc_ks))}}}', 
                xy=(0.5, 0.85), xycoords='axes fraction', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow'))

# Panel 3: Oscillation period vs K
ax = axes[1, 0]
osc_k = [k for k, p in zip(ks, osc_periods) if p > 0]
osc_p = [p for p in osc_periods if p > 0]
if osc_k:
    ax.plot(osc_k, osc_p, 'go-', markersize=10, linewidth=2)
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('Oscillation period (steps)')
    ax.set_title('Oscillation period vs K\nPeriod decreases with stronger coupling')
else:
    ax.text(0.5, 0.5, 'No oscillations detected', ha='center', transform=ax.transAxes)
ax.grid(True, alpha=0.3)

# Panel 4: Conceptual bifurcation diagram
ax = axes[1, 1]
# Sketch: as K increases, system goes from stable → oscillating → stable
# This looks like a "bubble" of oscillation
K_fine = np.linspace(5, 35, 200)
# Fit a Gaussian-like envelope for oscillation region
from scipy.stats import norm
if osc_ks:
    mu = np.mean(osc_ks)
    sigma_k = max(3, (max(osc_ks) - min(osc_ks)) / 4)
    envelope = 0.4 * np.exp(-0.5 * ((K_fine - mu) / sigma_k)**2)
    ax.fill_between(K_fine, -envelope, envelope, alpha=0.3, color='red')
    ax.plot(K_fine, envelope, 'r-', linewidth=2)
    ax.plot(K_fine, -envelope, 'r-', linewidth=2)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('Amplitude of r oscillation')
    ax.set_title(f'Conceptual bifurcation diagram\nOscillation "bubble" centered at K≈{mu:.0f}')
    ax.annotate('Stable', xy=(0.05, 0.85), xycoords='axes fraction', fontsize=12, color='blue')
    ax.annotate('OSCILLATING', xy=(0.35, 0.85), xycoords='axes fraction', fontsize=12, color='red')
    ax.annotate('Stable', xy=(0.75, 0.85), xycoords='axes fraction', fontsize=12, color='blue')
ax.grid(True, alpha=0.3)

fig.suptitle('R19Z: Bifurcation Analysis — The Oscillation Bubble\n'
             'α=0.9, σ=100, N=30 — Fine K scan reveals oscillation exists in a bounded region\n'
             'System is stable at both low and high K, oscillates at intermediate K',
             fontsize=13, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig('r19z_bifurcation.png', dpi=150, bbox_inches='tight')
print("Saved r19z_bifurcation.png")
