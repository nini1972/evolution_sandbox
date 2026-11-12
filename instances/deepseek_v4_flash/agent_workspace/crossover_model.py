"""
HYPOTHESIS: the window-dependent model selection (power law wins low-N, Kramers
wins high-N) is the signature of a CROSSOVER, not a fitting artifact.
Test a two-term model:  ln lam = c0 - c1*N - b*lnN   (Kramers + power law).
If it beats BOTH single-term models on full-range AIC AND resolves the
window-flip (c1, b both positive and consistent), the "single law" was the artifact.
"""
import json
import numpy as np
from scipy.optimize import minimize

D = json.load(open('km_barrier_corrected.json'))
rows = [r for r in D['rows'] if r['n_escaped'] > 0 and r['rate'] > 0]
Ns  = np.array([r['N'] for r in rows], float)
nev = np.array([r['n_escaped'] for r in rows], float)
tot = np.array([r['n_escaped']/r['rate'] for r in rows], float)
lnN = np.log(Ns)

def negll(params, form):
    c0, p1, p2 = params
    if form == 'kramers':   lam = np.exp(c0 - p1*Ns)                 # p1=c1, p2 ignored
    elif form == 'power':   lam = np.exp(c0 - p1*lnN)                # p1=b
    elif form == 'crossover': lam = np.exp(c0 - p1*Ns - p2*lnN)      # p1=c1, p2=b
    lam = np.clip(lam, 1e-300, None)
    return -float(np.sum(nev*np.log(lam) - lam*tot))

fits = {}
for form, x0 in [('kramers',[-3,0.008,0]), ('power',[3,1.55,0]), ('crossover',[-1,0.004,0.8])]:
    best = None
    for s0 in ([x0, [-2,0.005,1.0], [1,0.002,2.0]]):
        r = minimize(negll, s0, args=(form,), method='Nelder-Mead',
                     options=dict(maxiter=40000, xatol=1e-8, fatol=1e-8))
        if best is None or r.fun < best.fun: best = r
    k = 2 if form != 'crossover' else 3
    aic = 2*best.fun + 2*k
    fits[form] = dict(ll=-best.fun, k=k, aic=float(aic),
                      params=[float(x) for x in best.x], success=bool(best.success))

print('=== FULL-RANGE MODEL COMPARISON (censored survival likelihood) ===')
for form in ['kramers','power','crossover']:
    f = fits[form]
    print('%-10s LL=%10.2f  k=%d  AIC=%10.2f  params=%s'
          % (form, f['ll'], f['k'], f['aic'],
             np.round(f['params'],5)))

dK = fits['kramers']['aic'] - fits['crossover']['aic']
dP = fits['power']['aic']   - fits['crossover']['aic']
print('\ncrossover vs kramers: dAIC = %+.2f  (>0 => crossover better)' % dK)
print('crossover vs power  : dAIC = %+.2f  (>0 => crossover better)' % dP)
c1, b = fits['crossover']['params'][1], fits['crossover']['params'][2]
print('crossover params: c1(exponential) = %.5f , b(power) = %.4f' % (c1, b))

verdict = 'CROSSOVER WINS — single laws are window artifacts' if (dK > 2 and dP > 2) \
          else ('single Kramers adequate' if dK <= 0 else 'inconclusive')
print('\nVERDICT:', verdict)

# Re-fit crossover within each sub-window to check parameter stability now
def fit_cross(sel):
    N, n, T, lN = Ns[sel], nev[sel], tot[sel], lnN[sel]
    def f(p):
        lam = np.clip(np.exp(p[0]-p[1]*N-p[2]*lN), 1e-300, None)
        return -float(np.sum(n*np.log(lam)-lam*T))
    r = minimize(f, [-1,0.004,0.8], method='Nelder-Mead',
                 options=dict(maxiter=40000))
    return float(r.x[1]), float(r.x[2]), float(2*r.fun+2*3)

print('\n=== crossover params across N-windows (stability) ===')
sub = {}
for name, sel in [('40-320', Ns<=320), ('160-1280',(Ns>=160)&(Ns<=1280)),
                  ('320-1280', Ns>=320), ('40-1280', Ns<=1280)]:
    if sel.sum() < 3: continue
    c1w, bw, aicw = fit_cross(sel)
    print('N %-9s c1=%.5f  b=%.4f  AIC=%.2f' % (name, c1w, bw, aicw))
    sub[name] = dict(c1=c1w, b=bw, aic=aicw)

fits['subwindow_crossover'] = sub
fits['verdict'] = verdict
fits['delta_aic_cross_vs_kramers'] = dK
fits['delta_aic_cross_vs_power'] = dP
json.dump(fits, open('crossover_model.json','w'), indent=1)
print('\nsaved crossover_model.json')
