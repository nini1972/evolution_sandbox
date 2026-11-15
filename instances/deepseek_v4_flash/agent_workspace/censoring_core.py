#!/usr/bin/env python3
"""censoring_core.py — deterministic part only: 4 rival fits + profile CI for b.
Fast enough for the 120s local wall. Bootstrap goes to World C."""
import json
import numpy as np
from scipy.optimize import minimize

d = json.load(open("km_barrier_corrected.json"))
N = np.array([r["N"] for r in d["rows"]], float)
nesc = np.array([r["n_escaped"] for r in d["rows"]], float)
K, T = 256.0, 400.0
lnN = np.log(N)
n = len(N)

def make_lnlam(kind):
    if kind == 'kram':    return lambda p: p[0] - p[1] * N
    if kind == 'power':   return lambda p: p[0] - p[1] * lnN
    if kind == 'stretch': return lambda p: p[0] - p[1] * N ** p[2]
    if kind == 'cross':   return lambda p: p[0] - p[1] * N - p[2] * lnN
    raise ValueError(kind)

def negll(p, kind):
    lnlam = np.clip(make_lnlam(kind)(p), -80, 40)
    pe = np.clip(1.0 - np.exp(-np.exp(lnlam)), 1e-14, 1 - 1e-14)
    return -np.sum(nesc * np.log(pe) + (K - nesc) * np.log(1 - pe))

KINDS = {'kram': 2, 'power': 2, 'stretch': 3, 'cross': 3}
SEEDS = {
    'kram':    [[-3, 1e-3], [-2, 2e-3], [-4, 4e-3], [0, 5e-4]],
    'power':   [[2, 2.0], [4, 2.5], [1, 1.5], [6, 3.0]],
    'stretch': [[-3, 1e-3, 1.0], [-2, 2e-3, 0.7], [-4, 4e-3, 1.3], [0, 1e-3, 0.5]],
    'cross':   [[-3, 1e-3, 0.5], [-2, 2e-3, 1.0], [-4, 4e-3, 1.5], [0, 1e-3, 0.0]],
}

def fit(kind, seeds=None):
    best = None
    for s in (seeds or SEEDS[kind]):
        r = minimize(negll, np.array(s, float), args=(kind,), method='Nelder-Mead',
                     options=dict(maxiter=8000, maxfev=8000, xatol=1e-10, fatol=1e-10))
        if best is None or r.fun < best.fun:
            best = r
    return best

results = {}
print("=" * 78)
print("RIVAL ESCAPE-RATE LAWS | 8 sizes | exact binomial likelihood w/ censoring")
print("=" * 78)
for kind, k in KINDS.items():
    r = fit(kind)
    aic = 2 * k + 2 * r.fun
    bic = k * np.log(n) + 2 * r.fun
    results[kind] = dict(k=k, negll=float(r.fun), AIC=float(aic), BIC=float(bic),
                         params=[float(x) for x in r.x])
    print(f"  {kind:>8s} k={k} negll={r.fun:9.3f} AIC={aic:9.3f} BIC={bic:9.3f} par={np.round(r.x,5)}")

bestA = min(results.items(), key=lambda kv: kv[1]['AIC'])
bestB = min(results.items(), key=lambda kv: kv[1]['BIC'])
print(f"\n  AIC winner: {bestA[0]}    BIC winner: {bestB[0]}")
for kind in results:
    if kind != bestA[0]:
        print(f"    dAIC({kind} - {bestA[0]}) = {results[kind]['AIC'] - bestA[1]['AIC']:+7.3f}")

print("\n" + "=" * 78)
print("PROFILE LIKELIHOOD 95% CI for crossover exponent b")
print("=" * 78)
def profile_b(b):
    best = None
    for s in SEEDS['cross']:
        r = minimize(lambda p: negll([p[0], p[1], b], 'cross'), np.array([s[0], s[1]], float),
                     method='Nelder-Mead', options=dict(maxiter=8000, xatol=1e-10, fatol=1e-10))
        if best is None or r.fun < best.fun:
            best = r
    return best.fun

b_hat = results['cross']['params'][2]
ll_hat = -results['cross']['negll']
thresh = ll_hat - 0.5 * 3.841459
bs = np.linspace(-1.0, 3.0, 81)
lls = np.array([-profile_b(b) for b in bs])
inside = bs[lls >= thresh]
lo, hi = (float(inside.min()), float(inside.max())) if len(inside) else (float('nan'), float('nan'))
print(f"  b_hat = {b_hat:.4f}   profile 95% CI = [{lo:.3f}, {hi:.3f}]")
print(f"  b=0 (pure Kramers) in CI? {'YES -> Kramers NOT rejected' if lo <= 0 <= hi else 'NO  -> Kramers rejected'}")
print(f"  b=1 (pure 1/N prefactor) in CI? {'YES' if lo <= 1 <= hi else 'NO'}")
print(f"  b=0.896 (old naive 6-pt estimate) in CI? {'YES' if lo <= 0.896 <= hi else 'NO'}")

# Bayesian-ish posterior over b (flat prior, Laplace approx via profile)
w = np.exp(lls - lls.max())
w /= w.sum()
b_mean = float((bs * w).sum())
b_sd = float(np.sqrt(((bs - b_mean) ** 2 * w).sum()))
print(f"  profile-posterior over b: mean={b_mean:.3f}  sd={b_sd:.3f}")

json.dump(dict(rivals=results, AIC_winner=bestA[0], BIC_winner=bestB[0],
               b_hat=float(b_hat), b_profile_CI=[lo, hi], b_posterior=[b_mean, b_sd]),
          open("censoring_core.json", "w"), indent=1)
print("\nwrote censoring_core.json")
