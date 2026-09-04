import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

with open('r19z_seed_avg_data.json') as fp:
    seed_avg = json.load(fp)
with open('r19z_gs_dyn_data.json') as fp:
    gs_dyn = json.load(fp)

fig = plt.figure(figsize=(20, 16))

# Panel 1: Averaged cross-correlation vs f
ax1 = fig.add_subplot(3, 2, 1)
f_vals = [r['f'] for r in seed_avg]
corrs_avg = [r['avg_corr'] for r in seed_avg]
stds = [r['std_corr'] for r in seed_avg]
colors = ['#27ae60' if c > 0 else '#c0392b' for c in corrs_avg]
ax1.bar(range(len(f_vals)), corrs_avg, yerr=stds, color=colors, alpha=0.8,
        width=0.7, capsize=4)
ax1.axhline(y=0, color='black', linewidth=1.5)
ax1.set_xticks(range(len(f_vals)))
ax1.set_xticklabels(['%.3f' % f for f in f_vals], rotation=45, fontsize=9)
ax1.set_xlabel('Feed rate f', fontsize=11)
ax1.set_ylabel('Mean Cross-Correlation (2 seeds)', fontsize=11)
ax1.set_title('Resonance vs Anti-Resonance: The Resonance Island', fontsize=13, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Panel 2: |C| with error bars
ax2 = fig.add_subplot(3, 2, 2)
abs_avg = [abs(c) for c in corrs_avg]
ax2.errorbar(f_vals, abs_avg, yerr=stds, fmt='o-', color='#2d3561', linewidth=2,
             markersize=10, capsize=5, capthick=1.5)
ax2.set_xlabel('Feed rate f', fontsize=11)
ax2.set_ylabel('|Cross-Correlation|', fontsize=11)
ax2.set_title('Resonance Strength (error bars = seed variance)', fontsize=13, fontweight='bold')
ax2.grid(alpha=0.3)

# Panel 3: Zero-lag correlation
ax3 = fig.add_subplot(3, 2, 3)
zero_avg = [r['avg_zero_lag'] for r in seed_avg]
colors_z = ['#27ae60' if c > 0 else '#c0392b' for c in zero_avg]
ax3.bar(range(len(f_vals)), zero_avg, color=colors_z, alpha=0.8, width=0.7)
ax3.axhline(y=0, color='black', linewidth=1.5)
ax3.set_xticks(range(len(f_vals)))
ax3.set_xticklabels(['%.3f' % f for f in f_vals], rotation=45, fontsize=9)
ax3.set_xlabel('Feed rate f', fontsize=11)
ax3.set_ylabel('Zero-Lag Correlation', fontsize=11)
ax3.set_title('Simultaneous Correlation (zero lag)', fontsize=13, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Panel 4: GS dynamics (uncoupled) - complexity
ax4 = fig.add_subplot(3, 2, 4)
f_dyn = sorted([float(k) for k in gs_dyn.keys()])
comp_means = [gs_dyn[str(f)]['complexity_mean'] for f in f_dyn]
comp_stds = [gs_dyn[str(f)]['complexity_std'] for f in f_dyn]
ax4.plot(f_dyn, comp_means, 'b-o', label='mean complexity', linewidth=2, markersize=8)
ax4.fill_between(f_dyn,
                  [m - s for m, s in zip(comp_means, comp_stds)],
                  [m + s for m, s in zip(comp_means, comp_stds)],
                  alpha=0.2, color='blue')
ax4.set_xlabel('Feed rate f', fontsize=11)
ax4.set_ylabel('GS complexity (std of v)', fontsize=11, color='blue')
ax4.set_title('Uncoupled GS: Pattern Complexity', fontsize=13, fontweight='bold')
ax4.legend(loc='upper left', fontsize=9)
ax4.grid(alpha=0.3)

# Panel 5: GS autocorrelation - THE KEY MECHANISM
ax5 = fig.add_subplot(3, 2, 5)
ac10_vals = [gs_dyn[str(f)]['autocorr_10'] for f in f_dyn]
ac50_vals = [gs_dyn[str(f)]['autocorr_50'] for f in f_dyn]
ax5.plot(f_dyn, ac10_vals, 'g-o', label='autocorr(10 steps)', linewidth=2, markersize=8)
ax5.plot(f_dyn, ac50_vals, 'm-s', label='autocorr(50 steps)', linewidth=2, markersize=8)
ax5.axhline(y=0, color='black', linewidth=1, linestyle='--')
ax5.set_xlabel('Feed rate f', fontsize=11)
ax5.set_ylabel('Autocorrelation', fontsize=11)
ax5.set_title('GS Internal Timescale: Oscillatory Regime', fontsize=13, fontweight='bold')
ax5.legend(fontsize=9)
ax5.grid(alpha=0.3)

# Panel 6: Combined view - C and ac50 overlaid
ax6 = fig.add_subplot(3, 2, 6)
ax6.plot(f_vals, corrs_avg, 'r-o', label='Coupled C (best lag)', linewidth=2, markersize=10)
ax6_twin = ax6.twinx()
ax6_twin.plot(f_dyn, ac50_vals, 'b--s', label='Uncoupled ac(50)', linewidth=2, markersize=8, alpha=0.7)
ax6.axhline(y=0, color='black', linewidth=1, linestyle='--')
ax6.set_xlabel('Feed rate f', fontsize=11)
ax6.set_ylabel('Cross-Correlation', fontsize=11, color='red')
ax6_twin.set_ylabel('Autocorr(50)', fontsize=11, color='blue')
ax6.set_title('MECHANISM: C follows GS internal oscillation', fontsize=13, fontweight='bold')
lines1, labels1 = ax6.get_legend_handles_labels()
lines2, labels2 = ax6_twin.get_legend_handles_labels()
ax6.legend(lines1 + lines2, labels1 + labels2, fontsize=9)
ax6.grid(alpha=0.3)

plt.suptitle('R19Z Phase 8f: The Resonance Island\n'
             'Positive resonance occurs ONLY where GS has internal oscillatory dynamics (ac50<0)',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('r19z_phase_transition_deep.png', dpi=150, bbox_inches='tight')
plt.close()
print('Saved r19z_phase_transition_deep.png')