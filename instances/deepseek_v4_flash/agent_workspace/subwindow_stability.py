"""
FALSIFICATION TEST for the Kramers exponential law:
is the slope c1 in ln lam = c0 - c1*N CONSTANT across sub-windows of N?
If c1 drifts systematically with N-range, the "exponential law" is a local fit artifact.
Also compares Kramers vs power-law AIC *within each sub-window*.
"""
import json
import numpy as np

D = json.load(open('km_barrier_corrected.json'))
rows = [r for r in D['rows'] if r['n_escaped'] > 0 and r['rate'] > 0]
Ns  = np.array([r['N'] for r in rows], float)
nev = np.array([r['n_escaped'] for r in rows], float)
tot = np.array([r['n_escaped']/r['rate'] for r in rows], float)
lnN = np.log(Ns)
print('usable N:', [int(n) for n in Ns])

def fit(sel):
    """Return (c0,c1) Kramers MLE, (c0,b) power-law MLE, and AIC gap, on subset."""
    N, n, T = Ns[sel], nev[sel], tot[sel]
    lN = lnN[sel]
    # Kramers: ln lam = c0 - c1*N
    best = None
    for c0 in np.linspace(-8, 3, 111):
        for c1 in np.linspace(-0.03, 0.0, 121):
            lam = np.exp(c0 + c1*N)
            v = float(np.sum(n*np.log(lam) - lam*T))
            if best is None or v > best[0]: best = (v, c0, c1)
    llK, c0K, c1K = best
    # power law: ln lam = c0 - b*lnN
    best = None
    for c0 in np.linspace(-8, 20, 121):
        for b in np.linspace(0.0, 5.0, 101):
            lam = np.exp(c0 - b*lN)
            v = float(np.sum(n*np.log(lam) - lam*T))
            if best is None or v > best[0]: best = (v, c0, b)
    llP, c0P, bP = best
    aicK = -2*llK + 2*2
    aicP = -2*llP + 2*2
    return c0K, -c1K, aicK, bP, aicP

windows = [
    ('N 40-320   (low-N)',  Ns <= 320),
    ('N 160-1280 (mid-N)',  (Ns >= 160) & (Ns <= 1280)),
    ('N 320-1280 (hi-N)',   Ns >= 320),
    ('N 40-1280  (full)',   Ns <= 1280),
]
print('\n%-22s %9s %9s %10s %10s %9s' % ('window','c1(Kram)','AIC(Kram)','b(power)','AIC(pow)','dAIC K-P'))
res = {}
for name, sel in windows:
    if sel.sum() < 2:
        print('%-22s  -- too few points --' % name); continue
    c0K, c1K, aicK, bP, aicP = fit(sel)
    d = aicP - aicK   # >0 means Kramers better
    print('%-22s %9.5f %9.2f %10.4f %10.2f %9.2f' % (name, c1K, aicK, bP, aicP, d))
    res[name] = dict(n_points=int(sel.sum()), c1_kramers=float(c1K),
                     aic_kramers=float(aicK), b_power=float(bP),
                     aic_power=float(aicP), delta_aic_kramers_minus_power=float(d))

# stability verdict
c1s = [v['c1_kramers'] for v in res.values() if v['n_points'] >= 3]
if c1s:
    spread = (max(c1s)-min(c1s))/(np.mean(c1s)+1e-12)
    print('\nc1 across multi-point windows:', ['%.5f'%x for x in c1s])
    print('relative spread of c1 = %.1f%%' % (100*spread))
    res['c1_relative_spread'] = float(spread)
    res['c1_stable'] = bool(spread < 0.35)
    print('VERDICT: c1 is %s across N-sub-windows (%.1f%% spread).'
          % ('STABLE -> exponential law holds' if spread < 0.35
             else 'DRIFTING -> exponential law is a local artifact', 100*spread))
    wins = {k: v for k, v in res.items() if isinstance(v, dict)}
    if wins:
        best = max(wins.items(), key=lambda kv: kv[1]['delta_aic_kramers_minus_power'])[0]
        print('Best discriminating window for Kramers vs power law: %s' % best)
json.dump(res, open('subwindow_stability.json','w'), indent=1)
print('\nsaved subwindow_stability.json')
