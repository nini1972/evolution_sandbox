"""
Visualize the central finding: model selection between Kramers (ln lam ~ -N) and
power law (ln lam ~ -b lnN) FLIPS SIGN with the fitting window.
Left panel: survival/rate data with both model fits on full range.
Right panel: per-window AIC gap (Kramers - power law); sign indicates winner.
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

D = json.load(open('km_barrier_corrected.json'))
S = json.load(open('subwindow_stability.json'))
rows = [r for r in D['rows'] if r['n_escaped'] > 0 and r['rate'] > 0]
Ns  = np.array([r['N'] for r in rows], float)
nev = np.array([r['n_escaped'] for r in rows], float)
tot = np.array([r['n_escaped']/r['rate'] for r in rows], float)
lnN = np.log(Ns)

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))

# ---- LEFT: ln(rate) vs N with both full-range fits ----
ax[0].errorbar(Ns, np.log(nev/tot), yerr=1/np.sqrt(nev), fmt='o', color='k',
               capsize=3, label='data: ln(lambda)  (n_events/total_time)')
c0K, c1K = -3.0, 0.008
ax[0].plot(Ns, c0K - c1K*Ns, '--', color='crimson', lw=2,
           label='Kramers  ln lam = %.2f - %.5f N' % (c0K, c1K))
c0P, bP = 3.0, 1.55
ax[0].plot(Ns, c0P - bP*lnN, '-', color='navy', lw=2,
           label='Power law  ln lam = %.1f - %.2f lnN' % (c0P, bP))
ax[0].set_xlabel('N  (system size)')
ax[0].set_ylabel('ln(escape rate)')
ax[0].set_title('Both laws fit the same finite data (full range)')
ax[0].legend(fontsize=8.5); ax[0].grid(alpha=0.3)

# ---- RIGHT: per-window AIC gap ----
labels, gaps, cols = [], [], []
for k, v in S.items():
    if not isinstance(v, dict):
        continue
    labels.append(k.replace(' (', '\n('))
    gaps.append(-v['delta_aic_kramers_minus_power'])  # positive => Kramers better
    cols.append('crimson' if -v['delta_aic_kramers_minus_power'] > 0 else 'navy')
y = np.arange(len(labels))
ax[1].barh(y, gaps, color=cols, alpha=0.85)
ax[1].axvline(0, color='k', lw=1)
for i, g in enumerate(gaps):
    ax[1].text(g + (0.3 if g > 0 else -0.3), i, '%+.1f' % g,
               va='center', ha='left' if g > 0 else 'right', fontsize=9)
ax[1].set_yticks(y); ax[1].set_yticklabels(labels, fontsize=8.5)
ax[1].set_xlabel('AIC(power) - AIC(Kramers)   [>0 => Kramers wins]')
ax[1].set_title('MODEL SELECTION FLIPS WITH THE FITTING WINDOW')
ax[1].grid(alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('window_flip.png', dpi=140)
print('saved window_flip.png')
