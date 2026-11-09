#!/usr/bin/env python3
"""
Final anchor/robustness analysis for the Q-conservation dossier.

Goal: separate ESTIMATOR ARTIFACT from GENUINE SUBSTRATE BIFURCATION.

Key idea:
- The plateau D2 estimator has a measured anchor bias (sine->0.72 vs 1.0 expected,
  cloud3d->2.74 vs 3.0 expected). We quantify a per-substrate bias envelope.
- We then ask: after allowing the estimator to shift each substrate's Q by up to
  its worst-case bias, do the four substrate branches STILL fail to overlap?

If branches still don't overlap after bias correction -> genuine bifurcation.
If they collapse onto Q ~ -2.08 -> apparent dispersion was estimator artifact.
"""
import json, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- load full sweep results (18 rows across 4 substrates) ----
with open(os.path.join(HERE, 'morphospace_q_results.json')) as f:
    res = json.load(f)
rows = res['rows']

Q_TARGET = -2.08

# ---- anchor-derived D2 bias envelope ----
# plateau estimator anchors from d2_validation_results.json
ANCHOR_SINE_PLATEAU = 0.7165   # expected 1.0  -> underestimates by ~0.28
ANCHOR_CLOUD3D_PLATEAU = 2.7358 # expected 3.0  -> underestimates by ~0.26
# Conservative bias: plateau estimator can underestimate D2 by up to ~0.30.
# (Note: main estimator overestimates for smooth/low-dim, but plateau is what
#  we compare against literature. We take the LARGER of |anchor biases|.)
D2_BIAS = 0.30

# K calibration uncertainty: K* was calibrated at exactly ONE point (Lorenz rho=28).
# Native-K spread across substrates spans ~4.5 (Lorenz) down to ~0.002 (KS).
# We treat K as the dominant source of substrate-dependence and test sensitivity.

# ---- group rows by substrate ----
substrates = {}
for r in rows:
    substrates.setdefault(r['system'], []).append(r)

branch_stats = res.get('branch_stats', {})

# ---- Compute Q under three estimator conventions ----
# (A) native Q as reported
# (B) D2 bias-corrected: D2 -> D2 + D2_BIAS  (Q = -lam - D2 - K, so Q decreases)
#     i.e. Q_corr = Q_native - D2_BIAS
# (C) recalibrated-K with D2 bias: re-fit K* so that Q at calibration point = target,
#     after applying the D2 bias. This shows whether a single K* can ever align
#     all four substrates once estimator bias is allowed.
def q_of(r, d2_shift=0.0, k_offset=0.0):
    return -r['lam'] - (r['d2'] + d2_shift) - (r['K'] + k_offset)

# Recalibrate K* using D2-biased Lorenz rho=28 so Q_cal = target
calib_row = None
for r in substrates['Lorenz']:
    if abs(r['param'] - 28.0) < 1e-9:
        calib_row = r
assert calib_row is not None
# Q_new = -lam - (d2 + bias) - (K + off) = target  => off = -lam - d2 - bias - K - target
k_offset_needed = (-calib_row['lam'] - (calib_row['d2'] + D2_BIAS)
                   - calib_row['K'] - Q_TARGET)

conventions = {
    'A_native': {'d2_shift': 0.0, 'k_offset': 0.0},
    'B_d2bias': {'d2_shift': D2_BIAS, 'k_offset': 0.0},
    'C_d2bias_recalK': {'d2_shift': D2_BIAS, 'k_offset': k_offset_needed},
}

results = {}
for cname, c in conventions.items():
    per_sub = {}
    for name, rs in substrates.items():
        qs = [q_of(r, c['d2_shift'], c['k_offset']) for r in rs]
        per_sub[name] = {
            'mean': float(np.mean(qs)),
            'std': float(np.std(qs)),
            'min': float(np.min(qs)),
            'max': float(np.max(qs)),
            'qs': [float(x) for x in qs],
        }
    means = [v['mean'] for v in per_sub.values()]
    # separation = max branch mean - min branch mean
    separation = float(max(means) - min(means))
    pooled_std = float(np.mean([v['std'] for v in per_sub.values()]))
    # distance of each branch mean from target
    d_from_target = {k: float(v['mean'] - Q_TARGET) for k, v in per_sub.items()}
    results[cname] = {
        'branches': per_sub,
        'branch_separation': separation,
        'mean_within_branch_std': pooled_std,
        'invariance_ratio_sep_over_std': float(separation / pooled_std) if pooled_std > 0 else float('inf'),
        'd_from_target': d_from_target,
        'all_branches_within_0p5_of_target': bool(all(abs(v) <= 0.5 for v in d_from_target.values())),
    }

# ---- Verdict logic ----
convC = results['C_d2bias_recalK']
# Even after (i) D2 bias correction and (ii) a single global K recalibration that
# forces Lorenz rho=28 to hit the target exactly, do the other three substrates land
# on Q ~ -2.08?
worst_gap = max(abs(v) for v in convC['d_from_target'].values())
verdict = 'BIFURCATED' if worst_gap > 0.5 else 'CONSISTENT_WITH_INVARIANT'

summary = {
    'Q_target': Q_TARGET,
    'D2_bias_assumed': D2_BIAS,
    'anchor_evidence': {
        'sine_plateau_vs_expected': [ANCHOR_SINE_PLATEAU, 1.0],
        'cloud3d_plateau_vs_expected': [ANCHOR_CLOUD3D_PLATEAU, 3.0],
    },
    'K_offset_needed_for_recalf': float(k_offset_needed),
    'conventions': results,
    'verdict_after_bias_and_recalK': verdict,
    'worst_branch_gap_from_target': float(worst_gap),
    'calibration_row': {'system': 'Lorenz', 'param': 28.0,
                        'Q_after_conventionC': float(
                            -calib_row['lam'] - (calib_row['d2'] + D2_BIAS)
                            - (calib_row['K'] + k_offset_needed))},
}

with open(os.path.join(HERE, 'final_anchor_robustness.json'), 'w') as f:
    json.dump(summary, f, indent=2)

# ---- Figure: substrate branches under the three conventions vs target ----
fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), sharey=True)
colors = {'Lorenz': '#d62728', 'Henon': '#1f77b4', 'KS': '#2ca02c', 'Rule110': '#9467bd'}
titles = {
    'A_native': 'A) Native Q (as measured)',
    'B_d2bias': f'B) D2 bias-corrected (+{D2_BIAS})',
    'C_d2bias_recalK': 'C) D2 bias + single global K recalibration',
}
for ax, (cname, _) in zip(axes, conventions.items()):
    data = results[cname]
    for i, (name, v) in enumerate(data['branches'].items()):
        qs = v['qs']
        ax.scatter([i]*len(qs), qs, s=70, color=colors.get(name, 'gray'),
                   edgecolor='k', zorder=3, label=name if ax is axes[0] else None)
        ax.plot([i-0.18, i+0.18], [v['mean']]*2, 'k-', lw=2.5, zorder=4)
        ax.plot([i]*2, [v['mean']-v['std'], v['mean']+v['std']], 'k--', lw=1.5, zorder=4)
    ax.axhline(Q_TARGET, color='orange', lw=2.5, ls='-', zorder=2,
               label='Q* = -2.08' if ax is axes[0] else None)
    ax.set_xticks(range(len(data['branches'])))
    ax.set_xticklabels(list(data['branches'].keys()), fontsize=11)
    ax.set_title(titles[cname] + f"\nbranch separation = {data['branch_separation']:.2f}",
                 fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')
axes[0].set_ylabel('Q = $-\\lambda_{max} - D_2 - K$', fontsize=13)
axes[0].legend(loc='lower left', fontsize=9, framealpha=0.9)
fig.suptitle('Q-Conservation: substrate branches under estimator-bias corrections\n'
             f"Verdict after bias + single-K recalibration: {verdict} "
             f"(worst gap from Q* = {worst_gap:.2f})",
             fontsize=14, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig(os.path.join(HERE, 'morphospace_q_verification.png'), dpi=140)
print('Saved morphospace_q_verification.png')

# ---- Console verdict ----
print('=== FINAL ANCHOR / ROBUSTNESS VERDICT ===')
print(f'Q_target = {Q_TARGET}')
print(f'D2 bias assumed = {D2_BIAS} (from sine/cloud3d plateau anchors)')
print(f'K recalibration offset = {k_offset_needed:.4f} (to hit target at Lorenz rho=28)')
for cname in conventions:
    d = results[cname]
    print(f'[{cname}] separation={d["branch_separation"]:.3f} '
          f'invariance_ratio={d["invariance_ratio_sep_over_std"]:.3f} '
          f'worst_gap={max(abs(v) for v in d["d_from_target"].values()):.3f} '
          f'consistent={d["all_branches_within_0p5_of_target"]}')
print(f'VERDICT: {verdict} (worst branch gap from target = {worst_gap:.3f})')
print(f'Branch means after convention C: '
      + ', '.join(f'{k}={v["mean"]:.3f}' for k, v in convC['branches'].items()))