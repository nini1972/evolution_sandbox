import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('r19z_sigma_scan.json'))

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

colors_sigma = {'50': 'blue', '100': 'green', '200': 'red'}

# Panel 1: r_mean vs K for each sigma
ax = axes[0]
for sigma_key in sorted(data.keys(), key=lambda x: int(x.split('_')[1])):
    sigma = int(sigma_key.split('_')[1])
    ks = sorted([int(k) for k in data[sigma_key].keys()])
    r_means = [data[sigma_key][str(k)]['r_mean'] for k in ks]
    r_stds = [data[sigma_key][str(k)]['r_std'] for k in ks]
    color = colors_sigma[sigma_key.split('_')[1]]
    ax.errorbar(ks, r_means, yerr=r_stds, marker='o', color=color, 
               label=f'σ={sigma}', capsize=4, markersize=6, linewidth=2)

ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('Order parameter r (mean ± std)', fontsize=12)
ax.set_title('r(K) at different noise strengths σ\nThe synchronization curve shifts right with σ', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Panel 2: Oscillation strength heatmap-style
ax = axes[1]
for sigma_key in sorted(data.keys(), key=lambda x: int(x.split('_')[1])):
    sigma = int(sigma_key.split('_')[1])
    ks = sorted([int(k) for k in data[sigma_key].keys()])
    osc_strs = [data[sigma_key][str(k)]['osc_strength'] for k in ks]
    color = colors_sigma[sigma_key.split('_')[1]]
    ax.plot(ks, osc_strs, 'o-', color=color, label=f'σ={sigma}', markersize=8, linewidth=2)
    # Fill the oscillation region
    osc_ks = [k for k, s in zip(ks, osc_strs) if s > 0.15]
    if osc_ks:
        ax.axvspan(min(osc_ks)-1, max(osc_ks)+1, alpha=0.15, color=color)

ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('Oscillation strength', fontsize=12)
ax.set_title('Oscillation bubble shifts with σ\nHigher noise → bubble moves to higher K', fontsize=12)
ax.axhline(0.15, color='gray', linestyle='--', alpha=0.5, label='osc threshold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Add annotation
ax.annotate('σ=50: bubble at K≈8\nσ=100: bubble at K≈14\nσ=200: bubble at K≈30', 
            xy=(0.55, 0.7), xycoords='axes fraction', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightyellow'))

fig.suptitle('R19Z: The Resonance Bubble — Scaling with Noise Strength σ\n'
             'The oscillation region shifts to higher K as σ increases\n'
             'This confirms the oscillation is a RESONANCE — its location depends on the noise/signal balance',
             fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig('r19z_sigma_scaling.png', dpi=150, bbox_inches='tight')
print("Saved r19z_sigma_scaling.png")
