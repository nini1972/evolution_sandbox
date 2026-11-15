#!/usr/bin/env python3
"""
censoring_v2.py — the corrected audit. Four rival escape-rate laws, all 8 sizes,
right-censoring handled exactly, plus a calibration test of the AIC penalty.

BUG FIXED vs definitive_censoring.py: the 'Power' model there was implemented
with b=0, i.e. identical to Kramers. Its negll was a copy, not a fit.

Rivals:
  Kramers     ln lam = c0 - c1*N                  (2 par)
  Power       ln lam = c0 - b*ln N                (2 par)
  Stretched   ln lam = c0 - c1*N**beta            (3 par)  <-- the dangerous one
  Crossover   ln lam = c0 - c1*N - b*ln N         (3 par)

Likelihood: escapes are binomial, K = 256 trials, horizon T = 400:
  p(N) = 1 - exp(-lam(N)*T),  lnlam = ln lam + ln T
  LL = sum K*ln p + (K - n)*ln(1-p)   [exact for censored AND uncensored rows]
"""
import json
import numpy as np
from scipy.optimize import minimize

d = json.load(open("km_barrier_corrected.json"))
N = np.array([r["N"] for r in d["rows"]], float)
nesc = np.array([r["n_escaped"] for r in d["rows"]], float)
K = 256.0
T = 400.0
lnN = np.log(N)
n = len(N)

def make_lnlam(kind):
    if kind == 'kram':
        return lambda p: p[0] - p[1] * N
    if kind == 'power':
        return lambda p: p[0] - p[1] * lnN
    if kind == 'stretch':
        return lambda p: p[0] - p[1] * N ** p[2]
    if kind == 'cross':
        return lambda p: p[0] - p[1] * N - p[2] * lnN
    raise ValueError(kind)

def negll(p, kind):
    lnlam = np.clip(make_lnlam(kind)(p), -80, 40)
    p_esc = 1.0 - np.exp(-np.exp(lnlam))
    p_esc = np.clip(p_esc, 1e-14, 1 - 1e-14)
    return -np.sum(nesc * np.log(p_esc) + (K - nesc) * np.log(1 - p_esc))

KINDS = {'kram': 2, 'power': 2, 'stretch': 3, 'cross': 3}
SEEDS = {
    'kram':    [[-3, 1e-3], [-2, 2e-3], [-4, 4e-3], [0, 5e-4]],
    'power':   [[2, 2.0], [4, 2.5], [1, 1.5], [6, 3.0]],
    'stretch': [[-3, 1e-3, 1.0], [-2, 2e-3, 0.7], [-4, 4e-3, 1.3], [0, 1e-3, 0.5]],
    'cross':   [[-3, 1e-3, 0.5], [-2, 2e-3, 1.0], [-4, 4e-3, 1.5], [0, 1e-3, 0.0]],
}

def fit(kind):
    best = None
    for s in SEEDS[kind]:
        r = minimize(negll, np.array(s, float), args=(kind,), method='Nelder-Mead',
                     options=dict(maxiter=40000, maxfev=40000, xatol=1e-12, fatol=1e-12))
        if best is None or r.fun < best.fun:
            best = r
    return best

results = {}
print("=" * 80)
print("RIVAL ESCAPE-RATE LAWS  |  8 sizes  |  exact binomial likelihood w/ censoring")
print("=" * 80)
for kind, k in KINDS.items():
    r = fit(kind)
    aic = 2 * k + 2 * r.fun
    bic = k * np.log(n) + 2 * r.fun
    results[kind] = dict(k=k, negll=float(r.fun), AIC=float(aic), BIC=float(bic),
                         params=[float(x) for x in r.x])
    print(f"  {kind:>8s}  k={k}  negll={r.fun:9.3f}  AIC={aic:9.3f}  BIC={bic:9.3f}  "
          f"par={np.round(r.x, 5)}")

bestA = min(results.items(), key=lambda kv: kv[1]['AIC'])
print(f"\n  AIC winner: {bestA[0]}   BIC winner: "
      f"{min(results.items(), key=lambda kv: kv[1]['BIC'])[0]}")
for kind in results:
    if kind != bestA[0]:
        print(f"    dAIC({kind} - {bestA[0]}) = {results[kind]['AIC'] - bestA[1]['AIC']:+7.3f}")

# ------------------------------------------------ profile likelihood CI for b
print("\n" + "=" * 80)
print("PROFILE LIKELIHOOD 95% CI for the crossover exponent b")
print("=" * 80)
def profile_b(b):
    def f(p):
        return negll([p[0], p[1], b], 'cross')
    best = None
    for s in SEEDS['cross']:
        r = minimize(f, np.array([s[0], s[1]], float), method='Nelder-Mead',
                     options=dict(maxiter=30000, xatol=1e-12, fatol=1e-12))
        if best is None or r.fun < best.fun:
            best = r
    return best.fun

b_hat = results['cross']['params'][2]
ll_hat = -results['cross']['negll']
thresh = ll_hat - 0.5 * 3.841459   # 1-dof chi2, 95%
bs = np.linspace(-1.0, 3.0, 81)
lls = np.array([-profile_b(b) for b in bs])
inside = bs[lls >= thresh]
lo, hi = (inside.min(), inside.max()) if len(inside) else (np.nan, np.nan)
print(f"  b_hat = {b_hat:.4f}   profile 95% CI = [{lo:.3f}, {hi:.3f}]")
print(f"  b = 0 (pure Kramers) inside CI? {'YES -> cannot reject Kramers' if lo <= 0 <= hi else 'NO  -> Kramers rejected'}")
print(f"  b = 1 (pure 1/N prefactor) inside CI? {'YES' if lo <= 1 <= hi else 'NO'}")

# ------------------------------------- parametric bootstrap: is dAIC=9 trustworthy?
print("\n" + "=" * 80)
print("PARAMETRIC BOOTSTRAP — how often does AIC wrongly crown Crossover?")
print("=" * 80)
rng = np.random.default_rng(20241115)
def simulate(kind, params):
    lnlam = np.clip(make_lnlam(kind)(params), -80, 40)
    p_esc = 1 - np.exp(-np.exp(lnlam))
    return rng.binomial(int(K), p_esc).astype(float)

def fit_on(nesc_sim):
    global nesc
    save = nesc
    nesc = nesc_sim
    out = {}
    for kind in KINDS:
        r = fit(kind)
        out[kind] = 2 * KINDS[kind] + 2 * r.fun
    nesc = save
    return out

NREP = 300
for truth in ['kram', 'cross', 'stretch']:
    tp = results[truth]['params']
    wins = {'kram': 0, 'power': 0, 'stretch': 0, 'cross': 0}
    for _ in range(NREP):
        sim = simulate(truth, tp)
        aics = fit_on(sim)
        w = min(aics.items(), key=lambda kv: kv[1])[0]
        wins[w] += 1
    print(f"  truth={truth:>8s} -> AIC crowns: " +
          "  ".join(f"{k}:{100*v/NREP:5.1f}%" for k, v in wins.items()))

json.dump(dict(rivals=results, best_AIC=bestA[0], b_profile_CI=[float(lo), float(hi)]),
          open("censoring_v2.json", "w"), indent=1)
print("\nwrote censoring_v2.json")
