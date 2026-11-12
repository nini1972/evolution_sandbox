"""
PROPER CENSORED-SURVIVAL LIKELIHOOD AIC for the barrier rate law.
No raw times needed: total_t = n_events / rate, derived from saved JSON.

For each N: LL(model) = n_ev*ln(lam_pred) - lam_pred*total_t
            (exponential first-passage with right censoring)
AIC = -2*LL + 2*k  (lower is better)
"""
import json, math
import numpy as np

D = json.load(open('km_barrier_corrected.json'))
rows = D['rows']
data = []
for r in rows:
    n_ev = r['n_escaped']
    rate = r['rate']
    if rate <= 0 or n_ev <= 0:
        continue
    total_t = n_ev/rate          # total observed time, escaped + censored
    data.append((r['N'], n_ev, total_t))

Ns   = np.array([d[0] for d in data], float)
n_ev = np.array([d[1] for d in data], float)
tot  = np.array([d[2] for d in data], float)
lnN  = np.log(Ns)

def LL(c0, c1, x):            # ln lam = c0 + c1*x
    lam = np.exp(c0 + c1*x)
    return float(np.sum(n_ev*np.log(lam) - lam*tot))

models = {}
# 1) Kramers: ln lam = c0 - c1*N   (k=2)
best = None
for c0 in np.linspace(-6, 2, 81):
    for c1 in np.linspace(-0.02, 0.0, 81):
        v = LL(c0, c1, Ns)
        if best is None or v > best[0]:
            best = (v, c0, c1)
models['kramers  ln_lam = c0 - c1*N'] = (best[0], 2, best[1], best[2])
# 2) power law: ln lam = c0 - b*lnN  (k=2)
best = None
for c0 in np.linspace(-6, 12, 91):
    for b in np.linspace(0.0, 4.0, 81):
        v = LL(c0, -b, lnN)
        if best is None or v > best[0]:
            best = (v, c0, b)
models['powerlaw ln_lam = c0 - b*lnN'] = (best[0], 2, best[1], best[2])
# 3) horizon: b=0.5 fixed (k=1)
best = None
for c0 in np.linspace(-6, 12, 91):
    v = LL(c0, -0.5, lnN)
    if best is None or v > best[0]:
        best = (v, c0)
models['horizon  b=0.5 fixed'] = (best[0], 1, best[1], 0.5)

print('=== PROPER CENSORED-SURVIVAL LIKELIHOOD AIC ===')
print('N values used:', [int(n) for n in Ns], '  (N with 0 events dropped)')
out = {'data': data, 'models': {}}
for k, (ll, kpar, p1, p2) in sorted(models.items(), key=lambda kv: -kv[1][0]):
    aic = -2*ll + 2*kpar
    print('%-32s LL=%9.2f  k=%d  AIC=%9.2f  params=(%.4f, %.6f)' % (k, ll, kpar, aic, p1, p2))
    out['models'][k] = dict(LL=ll, k=kpar, AIC=aic, params=[p1, p2])
bestk = min(out['models'].items(), key=lambda kv: kv[1]['AIC'])
print('\nBEST BY PROPER AIC:', bestk[0], ' AIC=%.2f' % bestk[1]['AIC'])
c1 = out['models']['kramers  ln_lam = c0 - c1*N']['params'][1]
out['kramers_slope'] = float(-c1)
out['implied_barrier_per_osc'] = float(-c1)
out['best_by_proper_aic'] = bestk[0]
json.dump(out, open('aic_proper.json','w'), indent=1)
print('\nimplied Kramers barrier slope c1 = %.6f per unit N' % (-c1))
print('=> nucleation barrier U(N) ~ %.4f * N (in kT if SIG^2/2 ~ kT)' % (-c1))
