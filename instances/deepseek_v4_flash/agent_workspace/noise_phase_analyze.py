"""
noise_phase_analyze.py
Local post-processing for the World C noise-budget phase diagram job.
Reads world_c_results/noise_budget_phase.json (or local copy) and produces:
  - noise_budget_phase_final.png  (definitive figure, 4 panels)
  - noise_budget_summary.txt      (human-readable scientific summary)
Usage: python noise_phase_analyze.py [path_to_json]
"""
import json, sys, os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm

path = sys.argv[1] if len(sys.argv) > 1 else 'world_c_results/noise_budget_phase.json'
d = json.load(open(path))
sigmas = [str(s) for s in d['sigmas']]
Ns = d['Ns']
res = d['results']

print(f"Loaded {os.path.basename(path)}: {len(sigmas)} sigmas x {len(Ns)} N")
print(f"{'sigma':>6} {'beta':>7} {'r2_pow':>8} {'r2_arr':>8} {'winner':>10}")
for s in sigmas:
    r = res[s]
    print(f"{s:>6} {r['beta'] if r['beta'] is not None else float('nan'):7.3f} "
          f"{r['r2_power'] if r['r2_power'] is not None else float('nan'):8.3f} "
          f"{r['r2_arrhenius'] if r['r2_arrhenius'] is not None else float('nan'):8.3f} "
          f"{str(r['winner']):>10}")

# ---- definitive figure ----
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
cmap = cm.viridis
for i, s in enumerate(sigmas):
    r = res[s]
    c = cmap(i / max(len(sigmas)-1, 1))
    meds = [r['per_N'][str(N)]['median_km'] for N in Ns]
    cens = [r['per_N'][str(N)]['censored_frac'] for N in Ns]
    a = axes[0, 0]
    a.plot(Ns, meds, 'o-', color=c, lw=1.5, ms=5, label=f'$\\sigma$={s}')
    a.set_xscale('log'); a.set_yscale('log')
    a.set_xlabel('N'); a.set_ylabel('KM median $t_{esc}$')
    a.set_title('(a) Escape time vs N per noise level'); a.grid(True, which='both', alpha=0.3)

    b = axes[0, 1]
    b.plot(Ns, np.array(cens)*100, 'o--', color=c, lw=1.2, ms=4)
    b.set_xscale('log'); b.set_ylabel('% censored at Tmax')
    b.set_xlabel('N'); b.set_title('(b) Censoring diagnostics'); b.grid(True, alpha=0.3)

beta = np.array([res[s]['beta'] if res[s]['beta'] is not None else np.nan for s in sigmas])
r2a = np.array([res[s]['r2_arrhenius'] if res[s]['r2_arrhenius'] is not None else np.nan for s in sigmas])
r2p = np.array([res[s]['r2_power'] if res[s]['r2_power'] is not None else np.nan for s in sigmas])
sigv = np.array([float(s) for s in sigmas])

c = axes[1, 0]
c.plot(sigv, beta, 'ko-', lw=2, ms=7, label=r'$\beta$ (power-law)')
c.axhline(0.5, color='r', ls='--', lw=1.5, label='OA horizon ($\\beta$=0.5)')
c.axhline(1.0, color='gray', ls=':', lw=1, label='$\\beta$=1 (Arrhenius $\\sqrt{N}$)')
# crossover estimate via linear interpolation
for i in range(len(sigv)-1):
    if (beta[i]-0.5)*(beta[i+1]-0.5) < 0:
        s_star = sigv[i] + (0.5-beta[i])*(sigv[i+1]-sigv[i])/(beta[i+1]-beta[i])
        c.axvline(s_star, color='g', ls='-.', lw=1.2)
        c.text(s_star+0.01, 0.05, f'$\\sigma^*\\approx{s_star:.3f}$', color='g', fontsize=9)
c.set_xlabel('$\\sigma$ (injected noise)'); c.set_ylabel('exponent $\\beta$')
c.set_title('(c) Escape exponent vs noise budget: barrier vs horizon')
c.legend(fontsize=9); c.grid(True, alpha=0.3)

dd = axes[1, 1]
dd.plot(sigv, r2p, 'o-', color='tab:blue', label='$r^2$ power-law model')
dd.plot(sigv, r2a, 's-', color='tab:orange', label='$r^2$ Arrhenius model')
dd.axhline(0, color='k', ls=':')
dd.set_xlabel('$\\sigma$'); dd.set_ylabel('$r^2$ of log-linear fits')
dd.set_title('(d) Model discrimination'); dd.legend(fontsize=9); dd.grid(True, alpha=0.3)
axes[0, 0].legend(fontsize=7, ncol=2)
fig.suptitle('Noise-budget phase diagram of collective escape — reflexive Kuramoto (K0=5, $\\alpha$=1, Rth=0.5)',
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig('noise_budget_phase_final.png', dpi=140)
print('\nSaved noise_budget_phase_final.png')

# summary text
lines = ['=== NOISE-BUDGET PHASE DIAGRAM: COLLECTIVE ESCAPE ===',
         f'Protocol: reflexive Kuramoto, K0=5, alpha=1, Rth=0.5, Tmax={d["Tmax"]}, M={d["M"]}',
         '', f'{"sigma":>6} {"beta":>7} {"winner":>10}']
for s in sigmas:
    r = res[s]
    lines.append(f"{s:>6} {r['beta'] if r['beta'] is not None else float('nan'):7.3f} {str(r['winner']):>10}")
with open('noise_budget_summary.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print('Saved noise_budget_summary.txt')