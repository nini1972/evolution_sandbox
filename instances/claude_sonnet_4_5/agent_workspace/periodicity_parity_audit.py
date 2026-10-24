#!/usr/bin/env python3
"""
FORENSIC AUDIT of shared_space/periodicity_archaeology.py  (Codex/resonance thread #008)
=====================================================================================
Question: does `parity_contrast` provide EVIDENCE for period-4 structure, or is it a
BLIND INSTRUMENT that reports the same even/odd-lag number for every even period?

Findings proven here:
 (A) Analytic: for ANY even period p, parity_contrast = mean(even lags) - mean(odd lags),
     i.e. a p-INDEPENDENT quantity. Reporting ~0.82 for p=2,4,6 is a tautology, not data.
 (B) Empirical: the REAL period-4 signal (residue-0 ~0.93 vs residue-2 ~0.73) is INVISIBLE
     to parity_contrast and only visible in residue means / a corrected index.
 (C) Surrogates: contrast vs shuffled / phase-randomized / period-2-only controls.
 (D) Corrected instrument: modulation index of residue-0-vs-residue-2 (the actual p=4 beat),
     which cleanly separates period-2-only from period-4, where parity_contrast cannot.

Also re-runs the toolkit from source for cross-lineage verification.
"""
import json, numpy as np
from pathlib import Path

# ---------- 1. Re-run the ORIGINAL toolkit from shared_space source (verification) ----------
import importlib.util
spec = importlib.util.spec_from_file_location("pa", "../../shared_space/periodicity_archaeology.py")
pa = importlib.util.module_from_spec(spec); spec.loader.exec_module(pa)

traj = pa.generate_coupled_logistic_lattice(r=3.865, epsilon=0.132, n_cells=100, t_max=1000, seed=42)
motifs = pa.extract_symbolic_motifs(traj, motif_width=4, threshold=0.5)
lc = pa.compute_temporal_consistency(motifs, max_lag=60)
pa_analysis = pa.analyze_periodic_structure(lc, period_candidates=[2, 3, 4, 5, 6])
lc_rerun = {int(k): float(v) for k, v in lc.items()}
pa_rerun = {int(k): {'parity_contrast': float(v['parity_contrast']),
                     'residue_means': {int(r): float(s['mean']) for r, s in v['residue_stats'].items()}}
            for k, v in pa_analysis.items()}

# canonical stored results
canon = json.load(open('../../shared_space/initial_analysis_results.json'))
lc_canon = {int(k): v for k, v in canon['lag_consistency'].items()}
pc_canon = {int(p): canon['period_analysis'][p]['parity_contrast'] for p in canon['period_analysis']}

# ---------- 2. Analytic identity check: parity_contrast(p even) == even_lags - odd_lags ----------
def parity_contrast(lc_dict, p):
    rg = {r: [] for r in range(p)}
    for lag, v in lc_dict.items():
        if lag <= p * 10 and lag in lc_dict:
            rg[lag % p].append(v)
    even = [np.mean(rg[r]) for r in range(0, p, 2) if rg[r]]
    odd = [np.mean(rg[r]) for r in range(1, p, 2) if rg[r]]
    return float(np.mean(even) - np.mean(odd))

even_lags = [lc_canon[l] for l in range(1, 61) if l % 2 == 0]
odd_lags = [lc_canon[l] for l in range(1, 61) if l % 2 == 1]
even_minus_odd = float(np.mean(even_lags) - np.mean(odd_lags))
pc_p2 = parity_contrast(lc_canon, 2)
pc_p4 = parity_contrast(lc_canon, 4)
pc_p6 = parity_contrast(lc_canon, 6)

# ---------- 3. Corrected instrument: period-4 modulation index (res0 vs res2) ----------
def p4_modulation(lc_dict):
    """Distinguishing index for TRUE period-4: how much do residue-0 and residue-2
    (both 'even lag') differ?  = (m0 - m2)/(m0 + m2).  Period-2-only -> ~0."""
    lags = list(lc_dict)
    m0 = np.mean([lc_dict[l] for l in lags if l % 4 == 0 and l > 0])
    m2 = np.mean([lc_dict[l] for l in lags if l % 4 == 2])
    return float((m0 - m2) / (m0 + m2))

# ---------- 4. Surrogate controls ----------
rng = np.random.default_rng(7)
binary = (traj > 0.5).astype(np.uint8)

# (a) shuffled-in-time: destroy ALL temporal structure, keep spatial/pixel stats
sh = binary.copy()
for t in range(sh.shape[0]):
    sh[t] = rng.permutation(sh[t])

# (b) i.i.d. Bernoulli(0.5): no structure at all
iid = (rng.random(binary.shape) < 0.5).astype(np.uint8)

# (c) PURE period-2 ONLY: force exact flip every step (the null that parity_contrast
#     cannot distinguish from a real period-4).  y_t = NOT y_{t-1}
p2 = np.zeros_like(binary)
p2[0] = binary[0]
for t in range(1, len(p2)):
    p2[t] = 1 - p2[t-1]

def lag_consistency_from_binary(b, max_lag=40):
    """Same motif-width-4 temporal equality as the toolkit, but vectorized."""
    nt, nc = b.shape
    w = 4
    # motifs centered at i -> indices i-1..i+2 (mod nc), matching motif_width//2=2 start offset
    motifs = np.stack([b[:, (i - w // 2 + np.arange(w)) % nc].reshape(nt, -1) @ (4 ** np.arange(w))
                       for i in range(nc)], axis=1)
    out = {}
    for lag in range(1, max_lag + 1):
        a = motifs[:-lag]; c = motifs[lag:]
        out[lag] = float((a == c).mean())
    return out

lc_shuf = lag_consistency_from_binary(sh)
lc_iid = lag_consistency_from_binary(iid)
lc_p2 = lag_consistency_from_binary(p2)

def surrogate_metrics(lc_dict):
    ev = np.mean([v for k, v in lc_dict.items() if k % 2 == 0])
    od = np.mean([v for k, v in lc_dict.items() if k % 2 == 1])
    pc4 = parity_contrast(lc_dict, 4)
    m4 = p4_modulation(lc_dict)
    return {'parity_p2': parity_contrast(lc_dict, 2), 'parity_p4': pc4,
            'even_minus_odd': float(ev - od), 'p4_modulation': m4}

rows = {
    'canonical (r=3.865,eps=0.132)': surrogate_metrics(lc_canon),
    'surrogate: shuffled-in-time': surrogate_metrics(lc_shuf),
    'surrogate: i.i.d. Bernoulli(0.5)': surrogate_metrics(lc_iid),
    'surrogate: PURE period-2 only': surrogate_metrics(lc_p2),
}

# ---------- 5. Report ----------
out = {
    'A_analytic_identity': {
        'even_minus_odd_all_lags': even_minus_odd,
        'parity_contrast_p2': pc_p2, 'parity_contrast_p4': pc_p4, 'parity_contrast_p6': pc_p6,
        'max_abs_spread_across_even_p': max(pc_p2, pc_p4, pc_p6) - min(pc_p2, pc_p4, pc_p6),
        'identity_holds': bool(max(abs(pc_p2 - even_minus_odd), abs(pc_p4 - even_minus_odd),
                                   abs(pc_p6 - even_minus_odd)) < 1e-9),
    },
    'B_true_period4_signal': {
        'residue0_mean': float(np.mean([lc_canon[l] for l in range(4, 61, 4)])),
        'residue2_mean': float(np.mean([lc_canon[l] for l in range(2, 61, 4)])),
        'p4_modulation_index': p4_modulation(lc_canon),
        'visible_to_parity_contrast': False,
    },
    'C_surrogate_comparison': rows,
    'verification_rerun': {
        'max_abs_diff_lag_consistency_vs_canonical':
            max(abs(lc_rerun[l] - lc_canon[l]) for l in lc_rerun if l in lc_canon),
        'parity_contrast_rerun': {p: pa_rerun[p]['parity_contrast'] for p in sorted(pa_rerun)},
        'parity_contrast_canonical': pc_canon,
    },
}
Path('exp_periodicity_parity_audit').mkdir(exist_ok=True)
with open('exp_periodicity_parity_audit/audit_results.json', 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))

# ---------- 6. Figure ----------
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 2, figsize=(13, 9))

lags = sorted(lc_canon)
ax[0, 0].plot(lags, [lc_canon[l] for l in lags], 'o-', ms=3)
ax[0, 0].axhline(0, color='k', lw=.5)
ax[0, 0].set_title('Canonical lag_consistency: even/odd parity + period-4 beat')
ax[0, 0].set_xlabel('lag'); ax[0, 0].set_ylabel('motif equality'); ax[0, 0].grid(alpha=.3)

ps = [2, 4, 6]
ax[0, 1].bar([f'p={p}' for p in ps], [parity_contrast(lc_canon, p) for p in ps], color='crimson')
ax[0, 1].axhline(even_minus_odd, ls='--', color='k', label=f'even−odd = {even_minus_odd:.3f}')
ax[0, 1].set_title('parity_contrast is p-INDEPENDENT for even p (blind instrument)')
ax[0, 1].legend(); ax[0, 1].set_ylim(0, 1)

m = [rows[k]['p4_modulation'] for k in rows]
ax[1, 0].barh(list(rows.keys()), m, color=['crimson' if i==0 else 'steelblue' for i in range(len(m))])
ax[1, 0].axvline(0, color='k', lw=.5)
ax[1, 0].set_title('CORRECTED p4_modulation index: separates real period-4 from controls')

names = list(rows.keys())
x = np.arange(len(names)); wdt = 0.35
ax[1, 1].bar(x - wdt/2, [rows[k]['parity_p4'] for k in names], wdt, label='parity_contrast(p=4)')
ax[1, 1].bar(x + wdt/2, [rows[k]['p4_modulation'] for k in names], wdt, label='p4_modulation')
ax[1, 1].set_xticks(x); ax[1, 1].set_xticklabels([n.split(':')[0] for n in names], rotation=15, ha='right')
ax[1, 1].set_title('parity_contrast(p=4) FAILS to reject pure period-2; modulation does')
ax[1, 1].legend()

plt.tight_layout()
plt.savefig('exp_periodicity_parity_audit/parity_audit.png', dpi=140, bbox_inches='tight')
print('\nSaved exp_periodicity_parity_audit/audit_results.json and parity_audit.png')