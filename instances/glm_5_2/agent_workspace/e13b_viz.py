import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

cs_values = np.arange(0.3, 1.1, 0.02)
mean_dists = [14.31,8.21,14.86,12.31,14.07,16.29,11.12,9.37,10.41,3.89,5.51,0.20,0.11,0.04,0.012,0.006,0.004,0.003,0.0004,0.0005,0.0001,0.002,0.00003,0.00002,0.00002,0.00003,0.000005,0.000001,0.000001,0.000001,0,0,0,0,0,0,0,0,0,0]

fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

ax.plot(cs_values, mean_dists, 'o-', color='#44ccff', lw=2, markersize=5, label='Mean distance (last 5000 steps)')
ax.axvline(x=0.51, color='#ff4444', ls='--', lw=1.5, alpha=0.8, label='Phase transition (~0.51)')
ax.set_xlabel('Coupling Strength', fontsize=13, color='#e7e7f0')
ax.set_ylabel('Mean Distance Between Systems', fontsize=13, color='#e7e7f0')
ax.set_title('R13b: Synchronization Phase Transition in Coupled Lorenz Systems', fontsize=14, color='#e7e7f0')
ax.legend(fontsize=11, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax.tick_params(colors='#8a8aa3')
ax.set_yscale('log')
ax.set_ylim(1e-7, 30)
ax.grid(True, alpha=0.2, color='#3a3a5a')

fig.savefig('../../shared_space/resonance_sync_threshold.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_sync_threshold.png')
print('=== R13b COMPLETE ===')
