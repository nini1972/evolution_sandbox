import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('r19y_phase_data.json') as f:
    data = json.load(f)

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

sigmas = ['0.0', '1.0', '3.0', '5.0', '8.0']
colors = ['#44ffcc', '#ffaa44', '#ff6644', '#ff44aa', '#aa44ff']

for si, s in enumerate(sigmas):
    K = np.array(data[s]['K'])
    r = np.array(data[s]['r'])
    ax.plot(K, r, 'o-', color=colors[si], linewidth=2, markersize=6, 
            label=f'σ={s}', alpha=0.9)

# Reference: theoretical Kuramoto K_c = 2 for N->inf with uniform freq dist
ax.axvline(x=2.0, color='#ffffff', linestyle='--', alpha=0.4, label='Kuramoto K_c ≈ 2 (theory)')

ax.set_xlabel('K (coupling strength)', fontsize=14, color='#e7e7f0')
ax.set_ylabel('r (order parameter)', fontsize=14, color='#e7e7f0')
ax.set_title('SOC-Kuramoto r(K) at dt=0.02 (Numerically Stable)\nNo Over-coupling Decline — r is Monotonic in K', 
             fontsize=14, color='#44ffcc')
ax.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0', fontsize=11)
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.15)
ax.set_ylim(0, 1.05)
ax.set_xscale('log')

ax.annotate('r(K) is MONOTONIC\nNo "Echo Chamber Fragility"\nNo over-coupling decline', 
            xy=(20, 0.4), fontsize=12, color='#44ffcc', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#44ffcc', alpha=0.8))

plt.tight_layout()
fig.savefig('../../shared_space/resonance_stable_rscan.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved resonance_stable_rscan.png")
