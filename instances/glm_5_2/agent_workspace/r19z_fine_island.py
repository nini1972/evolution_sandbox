# R19Z Turn 14: Fine-Grained Resonance Island Boundary Mapping
# Using the CORRECT coupling from r19z_deep_lib.py
import numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from r19z_deep_lib import run_gs_sandpile, run_gs_only

# Fine f scan around the resonance island (f = 0.060 to 0.080)
f_values = np.linspace(0.058, 0.078, 21)  # step = 0.001
print(f'Fine scan: {len(f_values)} points from f={f_values[0]:.4f} to f={f_values[-1]:.4f}')

results = []
for i, f in enumerate(f_values):
    corrs = []
    zero_lags = []
    gs_stds = []
    for seed in [42, 123]:
        res = run_gs_sandpile(f, n_steps=2000, N_gap=10, burn_in=800, seed=seed)
        corrs.append(res['best_corr'])
        zero_lags.append(res['zero_lag'])
        gs_stds.append(res['gs_std'])
    avg_corr = float(np.mean(corrs))
    avg_zero = float(np.mean(zero_lags))
    avg_gstd = float(np.mean(gs_stds))
    sign = '+' if avg_corr > 0 else '-'
    results.append({
        'f': float(f),
        'C_mean': avg_corr,
        'C_std': float(np.std(corrs)),
        'zero_lag': avg_zero,
        'gs_std': avg_gstd,
        'sign': sign,
    })
    if i % 3 == 0:
        print(f'  f={f:.4f}: C={avg_corr:+.4f} +/- {np.std(corrs):.4f}, zero={avg_zero:+.4f}, gstd={avg_gstd:.4f}, sign={sign}')

# Also get uncoupled GS dynamics for same f values
print('\nUncoupled GS dynamics:')
uncoupled = []
for i, f in enumerate(f_values):
    comp_sig, mv_sig = run_gs_only(f, n_steps=2000, burn_in=800)
    s = int(2000 * 0.2)
    # Autocorrelation at lag 10 and 50
    def autocorr(x, lag):
        x = x - np.mean(x)
        if np.std(x) < 1e-10: return 0.0
        if lag >= len(x): return 0.0
        c = np.corrcoef(x[:len(x)-lag], x[lag:])[0,1]
        return 0.0 if np.isnan(c) else float(c)
    ac10 = autocorr(comp_sig[s:], 10)
    ac50 = autocorr(comp_sig[s:], 50)
    ac100 = autocorr(comp_sig[s:], 100)
    uncoupled.append({
        'f': float(f),
        'complexity': float(np.mean(comp_sig[s:])),
        'ac10': ac10, 'ac50': ac50, 'ac100': ac100,
    })
    if i % 3 == 0:
        print(f'  f={f:.4f}: comp={np.mean(comp_sig[s:]):.4f}, ac10={ac10:.3f}, ac50={ac50:.3f}, ac100={ac100:.3f}')

# Find island boundaries
signs = [1 if r['C_mean'] > 0 else -1 for r in results]
island_bounds = []
in_island = False
for i, sg in enumerate(signs):
    if sg > 0 and not in_island:
        start_f = results[i]['f']; in_island = True
    elif sg < 0 and in_island:
        island_bounds.append((start_f, results[i-1]['f'])); in_island = False
if in_island:
    island_bounds.append((start_f, results[-1]['f']))
print(f'\nResonance island bounds: {island_bounds}')

# Save data
with open('r19z_fine_island_data.json', 'w') as f:
    json.dump({'coupled': results, 'uncoupled': uncoupled, 'island_bounds': island_bounds}, f, indent=2)

# === Visualization ===
fig = plt.figure(figsize=(18, 14))
gs = GridSpec(4, 2, figure=fig, hspace=0.4, wspace=0.3)

fs = [r['f'] for r in results]
cs = [r['C_mean'] for r in results]
cs_err = [r['C_std'] for r in results]
zs = [r['zero_lag'] for r in results]
gstds = [r['gs_std'] for r in results]

uf = [u['f'] for u in uncoupled]
ucomp = [u['complexity'] for u in uncoupled]
uac10 = [u['ac10'] for u in uncoupled]
uac50 = [u['ac50'] for u in uncoupled]
uac100 = [u['ac100'] for u in uncoupled]

# Panel 1: C vs f (coupled, fine)
ax1 = fig.add_subplot(gs[0, :])
ax1.errorbar(fs, cs, yerr=cs_err, fmt='o-', ms=4, capsize=3, color='darkblue', lw=1.5)
ax1.axhline(0, color='gray', ls='--', lw=0.5)
ax1.set_xlabel('f (Gray-Scott feed rate)', fontsize=12)
ax1.set_ylabel('Cross-correlation C', fontsize=12)
ax1.set_title('Resonance Island: Fine-Grained Boundary Mapping', fontsize=14, fontweight='bold')
for (s, e) in island_bounds:
    ax1.axvspan(s, e, alpha=0.15, color='green')
ax1.annotate('RESONANCE\nISLAND', xy=(0.5, 0.7), xycoords='axes fraction',
            fontsize=11, ha='center', color='green', fontweight='bold')

# Panel 2: Zero-lag correlation
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(fs, zs, 's-', ms=4, color='darkred')
ax2.axhline(0, color='gray', ls='--', lw=0.5)
ax2.set_xlabel('f'); ax2.set_ylabel('Zero-lag correlation')
ax2.set_title('Zero-lag Cross-correlation')
for (s, e) in island_bounds:
    ax2.axvspan(s, e, alpha=0.15, color='green')

# Panel 3: GS std (coupled)
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(fs, gstds, 'o-', ms=4, color='purple')
ax3.set_xlabel('f'); ax3.set_ylabel('GS std(v)')
ax3.set_title('GS Pattern Complexity (Coupled)')
for (s, e) in island_bounds:
    ax3.axvspan(s, e, alpha=0.15, color='green')

# Panel 4: Uncoupled complexity
ax4 = fig.add_subplot(gs[2, 0])
ax4.plot(uf, ucomp, 'o-', ms=4, color='orange')
ax4.set_xlabel('f'); ax4.set_ylabel('Mean std(v)')
ax4.set_title('Uncoupled GS: Pattern Complexity')
for (s, e) in island_bounds:
    ax4.axvspan(s, e, alpha=0.15, color='green')

# Panel 5: Uncoupled autocorrelation
ax5 = fig.add_subplot(gs[2, 1])
ax5.plot(uf, uac10, 'o-', ms=4, label='ac(10)', color='orange')
ax5.plot(uf, uac50, 's-', ms=4, label='ac(50)', color='red')
ax5.plot(uf, uac100, '^-', ms=4, label='ac(100)', color='darkred')
ax5.axhline(0, color='gray', ls='--', lw=0.5)
ax5.set_xlabel('f'); ax5.set_ylabel('Autocorrelation')
ax5.set_title('Uncoupled GS: Internal Dynamics')
ax5.legend()
for (s, e) in island_bounds:
    ax5.axvspan(s, e, alpha=0.15, color='green')

# Panel 6: Overlay — C vs ac50
ax6 = fig.add_subplot(gs[3, :])
ax6t = ax6.twinx()
ax6.plot(fs, cs, 'o-', ms=4, color='darkblue', label='C (coupled)')
ax6.axhline(0, color='gray', ls='--', lw=0.5)
ax6t.plot(uf, uac50, 's-', ms=4, color='red', label='ac(50) (uncoupled)')
ax6t.axhline(0, color='red', ls='--', lw=0.5, alpha=0.3)
ax6.set_xlabel('f (feed rate)', fontsize=12)
ax6.set_ylabel('Cross-correlation C', color='darkblue', fontsize=12)
ax6t.set_ylabel('Autocorrelation ac(50)', color='red', fontsize=12)
ax6.set_title('The Mechanism: C>0 precisely where ac(50)<0 (internal oscillation)', fontsize=13, fontweight='bold')
for (s, e) in island_bounds:
    ax6.axvspan(s, e, alpha=0.1, color='green')
l1, la1 = ax6.get_legend_handles_labels(); l2, la2 = ax6t.get_legend_handles_labels()
ax6.legend(l1+l2, la1+la2, loc='upper left')

fig.suptitle('R19Z Turn 14: Fine-Grained Resonance Island — Boundary Structure & Mechanism',
             fontsize=16, fontweight='bold')
fig.savefig('r19z_fine_island.png', dpi=150, bbox_inches='tight')
print('\nSaved r19z_fine_island.png')
print('Done!')
