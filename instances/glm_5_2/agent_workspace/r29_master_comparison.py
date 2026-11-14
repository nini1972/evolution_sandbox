"""
R29 Master Comparison: One-Way Resonance Gap vs Bidirectional Anticorrelation
The fundamental asymmetry in timescale-separated coupling.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json

# ---- Load R28 bidirectional data ----
with open('world_c_results/r28_bidirectional_results.json') as f:
    r28 = json.load(f)

# ---- Load R27 bidirectional data (earlier sweep) ----
with open('world_c_results/r27_bidirectional_results.json') as f:
    r27 = json.load(f)

# ---- Load R19Z one-way anti-resonance matrix ----
with open('r19z_anti_resonance.json') as f:
    r19z = json.load(f)

# ---- Extract R28 by feedback level ----
fb_levels = [0.0, 0.1, 0.3, 0.5]
fb_labels = ['fb=0.0', 'fb=0.1', 'fb=0.3', 'fb=0.5']
fb_colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']

r28_by_fb = {}
for fb in fb_levels:
    entries = [e for e in r28 if abs(e['feedback_frac'] - fb) < 1e-6]
    entries.sort(key=lambda x: x['N_gap'])
    r28_by_fb[fb] = {
        'N_gaps': [e['N_gap'] for e in entries],
        'xcorr': [e['peak_cross_corr'] for e in entries],
        'lag': [e['peak_lag'] for e in entries],
    }

# ---- Extract R27 by feedback level ----
r27_by_fb = {}
for fb in [0.0, 0.1, 0.5]:
    entries = [e for e in r27 if abs(e['feedback_frac'] - fb) < 1e-6]
    entries.sort(key=lambda x: x['N_gap'])
    r27_by_fb[fb] = {
        'N_gaps': [e['N_gap'] for e in entries],
        'xcorr': [e['peak_cross_corr'] for e in entries],
    }

# ---- R19Z one-way: extract mean cross-corr at each N_gap (averaged over forcing amps) ----
r19z_N_gaps = r19z['N_gaps']
C_matrix = np.array(r19z['C_matrix'])  # shape (n_amps, n_gaps)
# Use the absolute value mean
r19z_mean_abs = np.mean(np.abs(C_matrix), axis=0)
# Also get max cross-corr at each N_gap
r19z_max_abs = np.max(np.abs(C_matrix), axis=0)

# ============ FIGURE ============
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.suptitle('R29: Resonance Gap Asymmetry — One-Way vs Bidirectional Coupling', 
             fontsize=16, fontweight='bold', y=0.98)

# ---- Panel A: R28 Bidirectional — cross-corr vs N_gap ----
ax = axes[0, 0]
for i, fb in enumerate(fb_levels):
    d = r28_by_fb[fb]
    ax.plot(d['N_gaps'], d['xcorr'], 'o-', color=fb_colors[i], 
            label=fb_labels[i], linewidth=2, markersize=8)
ax.set_xlabel('Timescale Gap N', fontsize=12)
ax.set_ylabel('Peak Cross-Correlation |C|', fontsize=12)
ax.set_title('A) Bidirectional: Crossover (R28) — C decreases with N', fontsize=13)
ax.set_xscale('log')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# ---- Panel B: R19Z One-Way — |cross-corr| vs N_gap ----
ax = axes[0, 1]
ax.plot(r19z_N_gaps, r19z_mean_abs, 's-', color='#9C27B0', 
        label='Mean |C| (over all forcing)', linewidth=2, markersize=8)
ax.fill_between(r19z_N_gaps, np.zeros_like(r19z_mean_abs), r19z_max_abs, 
               alpha=0.2, color='#9C27B0', label='Max |C| envelope')
ax.set_xlabel('Timescale Gap N', fontsize=12)
ax.set_ylabel('|Cross-Correlation|', fontsize=12)
ax.set_title('B) One-Way: Resonance Gap (R19Z) — C increases with N', fontsize=13)
ax.set_xscale('log')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# ---- Panel C: Direct comparison — R28 fb=0 vs R19Z mean ----
ax = axes[1, 0]
# R28 fb=0
d28 = r28_by_fb[0.0]
ax.plot(d28['N_gaps'], d28['xcorr'], 'o-', color='#F44336', 
        label='Bidirectional (R28, fb=0)', linewidth=2.5, markersize=8)
# R28 fb=0.5
d28_5 = r28_by_fb[0.5]
ax.plot(d28_5['N_gaps'], d28_5['xcorr'], '^-', color='#FF9800', 
        label='Bidirectional (R28, fb=0.5)', linewidth=2.5, markersize=8)
# R19Z mean abs
ax.plot(r19z_N_gaps, r19z_mean_abs, 's--', color='#9C27B0', 
        label='One-Way (R19Z, mean |C|)', linewidth=2.5, markersize=8)
ax.set_xlabel('Timescale Gap N', fontsize=12)
ax.set_ylabel('|Peak Cross-Correlation|', fontsize=12)
ax.set_title('C) The Asymmetry: Opposite Trends', fontsize=13)
ax.set_xscale('log')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.annotate('Bidirectional:\nC ∝ 1/N (decreasing)', 
            xy=(20, 0.21), fontsize=11, color='#F44336',
            arrowprops=dict(arrowstyle='->', color='#F44336'),
            xytext=(3, 0.35))
ax.annotate('One-Way:\nC increases with N', 
            xy=(50, r19z_mean_abs[4]), fontsize=11, color='#9C27B0',
            arrowprops=dict(arrowstyle='->', color='#9C27B0'),
            xytext=(2, 0.15))

# ---- Panel D: R27 vs R28 convergence check ----
ax = axes[1, 1]
# R28 fb=0
d28 = r28_by_fb[0.0]
ax.plot(d28['N_gaps'], d28['xcorr'], 'o-', color='#2196F3', 
        label='R28 fb=0.0', linewidth=2, markersize=7)
# R27 fb=0
d27 = r27_by_fb[0.0]
ax.plot(d27['N_gaps'], d27['xcorr'], 'D--', color='#2196F3', 
        label='R27 fb=0.0', linewidth=1.5, markersize=7, alpha=0.7)
# R28 fb=0.5
d28_5 = r28_by_fb[0.5]
ax.plot(d28_5['N_gaps'], d28_5['xcorr'], 'o-', color='#F44336', 
        label='R28 fb=0.5', linewidth=2, markersize=7)
# R27 fb=0.5
d27_5 = r27_by_fb[0.5]
ax.plot(d27_5['N_gaps'], d27_5['xcorr'], 'D--', color='#F44336', 
        label='R27 fb=0.5', linewidth=1.5, markersize=7, alpha=0.7)
ax.set_xlabel('Timescale Gap N', fontsize=12)
ax.set_ylabel('|Peak Cross-Correlation|', fontsize=12)
ax.set_title('D) Reproducibility: R27 vs R28', fontsize=13)
ax.set_xscale('log')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('r29_master_comparison.png', dpi=150, bbox_inches='tight')
print("Saved r29_master_comparison.png")

# ---- Also save summary metrics ----
summary = {
    'discovery': 'Resonance Gap Asymmetry: One-Way coupling shows C increasing with N_gap (resonance buildup), while Bidirectional coupling shows C decreasing with N_gap (destructive interference / anticorrelation).',
    'r28_bidirectional': {
        'trend': 'DECREASING with N_gap',
        'fb_0_peak_at_N1': r28_by_fb[0.0]['xcorr'][0],
        'fb_0_at_N100': r28_by_fb[0.0]['xcorr'][-1],
        'ratio_N1_to_N100': r28_by_fb[0.0]['xcorr'][0] / r28_by_fb[0.0]['xcorr'][-1],
    },
    'r19z_oneway': {
        'trend': 'INCREASING with N_gap (mean |C|)',
        'mean_abs_at_N1': float(r19z_mean_abs[0]),
        'mean_abs_at_N100': float(r19z_mean_abs[-1]),
    },
    'key_insight': 'The direction of information flow determines whether timescale separation builds or destroys resonance. This is a fundamental asymmetry in coupled nonlinear systems.',
}
with open('r29_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("Saved r29_summary.json")
print(json.dumps(summary, indent=2))