import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# dt convergence data
dt_data = [
    (0.1000, 0.2779),
    (0.0500, 0.3838),
    (0.0200, 0.6233),
    (0.0100, 0.8953),
    (0.0050, 0.9678),
    (0.0020, 0.9888),
    (0.0010, 0.9948),
]
dts = [d[0] for d in dt_data]
rs = [d[1] for d in dt_data]

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#0a0a1a')

# Panel 1: dt convergence
ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
ax1.plot(dts, rs, 'o-', color='#44ffcc', linewidth=2.5, markersize=10)
ax1.axhline(y=0.99, color='#ff6644', linestyle='--', alpha=0.7, label='r → 0.99 (true limit)')
ax1.set_xlabel('dt (time step)', fontsize=14, color='#e7e7f0')
ax1.set_ylabel('r (order parameter)', fontsize=14, color='#e7e7f0')
ax1.set_title('DT CONVERGENCE TEST\nK=80, σ=160 — The "Ceiling" Vanishes as dt→0', 
              fontsize=13, color='#44ffcc', fontweight='bold')
ax1.set_xscale('log')
ax1.legend(facecolor='#1a1a2a', edgecolor='#8a8aa3', labelcolor='#e7e7f0', fontsize=11)
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.15)
ax1.set_ylim(0, 1.05)
ax1.annotate('Forward Euler\nartifact zone', xy=(0.06, 0.33), fontsize=11, color='#ff6644',
            bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#ff6644', alpha=0.8))
ax1.annotate('True physics\nr ≈ 0.99', xy=(0.002, 0.99), fontsize=11, color='#44ffcc',
            bbox=dict(boxstyle='round', facecolor='#1a1a2a', edgecolor='#44ffcc', alpha=0.8))

# Panel 2: The "ceiling" coincides with Euler stability limit
ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
dt_orig = 0.1
K_crit_euler = 2.0 / dt_orig  # = 20
K_max_measured = 19.6

bar_labels = ['K_max\n(measured\n"ceiling")', 'K_crit\n(Euler\nstability)']
bar_values = [K_max_measured, K_crit_euler]
colors = ['#ff6644', '#ffaa44']
bars = ax2.bar(bar_labels, bar_values, color=colors, edgecolor='#ffffff', linewidth=1.5, width=0.5)
ax2.set_ylabel('K value', fontsize=14, color='#e7e7f0')
ax2.set_title('THE "CEILING" = EULER STABILITY LIMIT\nK_max ≈ K_crit = 2/dt (within 2%)', 
              fontsize=13, color='#ff6644', fontweight='bold')
ax2.tick_params(colors='#8a8aa3')
for bar, val in zip(bars, bar_values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
             f'{val:.1f}', ha='center', fontsize=14, color='#e7e7f0', fontweight='bold')
ax2.set_ylim(0, 25)
ax2.annotate('Δ = 2%', xy=(0.5, 20), ha='center', fontsize=16, color='#44ffcc', fontweight='bold')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_19y_ceiling_debunked.png', dpi=150, 
           bbox_inches='tight', facecolor='#0a0a1a')
print("Saved resonance_19y_ceiling_debunked.png")
