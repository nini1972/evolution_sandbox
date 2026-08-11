import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('r19y_data.json') as f:
    results = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('#0a0a1a')
ax1, ax2 = axes
ax1.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')

dt_values = ['0.1', '0.05', '0.02']
colors = ['#ff4444', '#ff44aa', '#44ffcc']
markers = ['o', 's', '^']

for di, dt in enumerate(dt_values):
    K = np.array(results[dt]['K'])
    r = np.array(results[dt]['r'])
    peak_r = np.max(r)
    final_r = r[-1]
    decline = peak_r - final_r
    print(f"dt={dt}: peak={peak_r:.4f}, final={final_r:.4f}, decline={decline:.4f}")
    ax1.plot(K, r, f'{markers[di]}-', color=colors[di], linewidth=1.5, 
             markersize=4, label=f'dt={dt} (K_crit={2/float(dt):.0f})')

for dt, c in zip(dt_values, colors):
    ax1.axvline(x=2/float(dt), color=c, linestyle=':', alpha=0.3)

ax1.set_title('r(K) at Different Time Steps (sigma=5)', fontsize=14, color='#44ffcc')
ax1.set_xlabel('K (coupling strength)', color='#e7e7f0')
ax1.set_ylabel('r (order parameter)', color='#e7e7f0')
ax1.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15)
ax1.set_ylim(0, 1.05)
ax1.annotate('Dotted lines: K_crit=2/dt\n(Euler stability limit)', xy=(30, 0.5), 
             fontsize=10, color='#ff44aa', bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#ff44aa', alpha=0.8))

# Panel 2: Stability diagram
K_r = np.linspace(0, 50, 200)
dt_r = np.linspace(0.005, 0.15, 200)
K_g, dt_g = np.meshgrid(K_r, dt_r)
stab = K_g * dt_g
ax2.contourf(K_g, dt_g, stab, levels=[0,1,2,3,5,10], colors=['#44ffcc','#44ffcc','#ffaa44','#ff4444','#660000'], alpha=0.7)
ax2.contour(K_g, dt_g, stab, levels=[2], colors='#ffffff', linewidths=2, linestyles='--')
ax2.set_title('Forward Euler Stability: K*dt < 2', fontsize=14, color='#44ffcc')
ax2.set_xlabel('K (coupling strength)', color='#e7e7f0')
ax2.set_ylabel('dt (time step)', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.annotate('STABLE', xy=(5, 0.01), fontsize=16, color='#44ffcc', fontweight='bold')
ax2.annotate('UNSTABLE', xy=(30, 0.08), fontsize=16, color='#ff4444', fontweight='bold')

fig.suptitle('R19y: Numerical Stability Correction - "Over-coupling Decline" is an Integration Artifact', 
             fontsize=16, color='#44ffcc', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_correction.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_correction.png')
