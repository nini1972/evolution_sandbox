#!/usr/bin/env python3
"""
definitive_censoring.py — does right-censoring fabricate the crossover?

The two artifacts in this workspace contradict each other:
  crossover_audit.md      -> "CROSSOVER wins, b = 0.86 +/- 0.08"   (6 uncensored pts)
  km_barrier_corrected.json -> "KRAMERS (true nucleation barrier)" (8 pts, censored)

My hypothesis: the crossover exponent is a CENSORING ARTIFACT. Dropping the
right-censored observations (N=2560, 5120: zero escapes in T=400) removes the
points that pin down the large-N slope, so the remaining 6 points look like they
curve, and a -b*lnN term absorbs the curvature.

We test this head-on with a proper binomial (censored) likelihood.
"""
import json
import numpy as np
from scipy.optimize import minimize

d = json.load(open("km_barrier_corrected.json"))
N   = np.array([r["N"] for r in d["rows"]], float)
nesc= np.array([r["n_escaped"] for r in d["rows"]], float)
NT  = 256.0          # trials per size
T   = 400.0          # observation horizon
n   = len(N)
unc = nesc > 0       # uncensored rows

print("=" * 78)
print("RAW DATA  (T = 400, 256 trials per size)")
print("=" * 78)
print(f"{'N':>6} {'n_esc':>6} {'censor%':>8} {'rate':>12} {'ln rate':>10}")
for i in range(n):
    lr = np.log(nesc[i] / (d['rows'][i]['km_rmst'] * NT)) if nesc[i] > 0 else -np.inf
    print(f"{N[i]:>6.0f} {nesc[i]:>6.0f} {100*(1-nesc[i]/NT):>8.2f} "
          f"{nesc[i]/(d['rows'][i]['km_rmst']*NT):>12.3e} {lr:>10.4f}")
print(f"\n  uncensored rows: {int(unc.sum())} of {n}   "
      f"(N={N[~unc].astype(int).tolist()} are FULLY censored -> only lower bounds)")

# ---------------------------------------------------------------- naive 6-pt fit
lnN = np.log(N)
lnlam = np.log(nesc / (np.array([r['km_rmst'] for r in d['rows']]) * NT))
lnlam[~unc] = np.nan

def fit_naive(b):
    """fit c0,c1 with b fixed, on uncensored rows only; return RSS, c0, c1"""
    m = unc
    A = np.column_stack([np.ones(m.sum()), -N[m]])
    y = lnlam[m] + b * lnN[m]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    return float(r @ r), coef[0], coef[1]

def fit_naive_best():
    from scipy.optimize import minimize_scalar
    r = minimize_scalar(lambda b: fit_naive(b)[0], bounds=(-2, 4), method='bounded')
    rss, c0, c1 = fit_naive(r.x)
    return r.x, c0, c1, rss

b_naive, c0n, c1n, rss_n = fit_naive_best()
rss_k_n = fit_naive(0.0)[0]
k_n = 3
AIC_n = 2*k_n + (unc.sum()) * np.log(rss_n / unc.sum())
AIC_k_n = 2*2 + (unc.sum()) * np.log(rss_k_n / unc.sum())

print("\n" + "=" * 78)
print("(A) NAIVE 6-POINT ln(rate) FIT  — reproduces the old audit")
print("=" * 78)
print(f"  crossover: c0={c0n:+.4f}  c1={c1n:.6f}  b={b_naive:+.4f}   RSS={rss_n:.6f}")
print(f"  Kramers  : c1={fit_naive(0.0)[2]:.6f}                    RSS={rss_k_n:.6f}")
print(f"  -> naive fit says b = {b_naive:+.3f}  (b>0 => 'crossover' with power prefactor)")
print(f"     dRSS(Kramers - crossover) = {rss_k_n - rss_n:+.4f}")

# ---------------------------------------------------- censored binomial likelihood
def negll(p, model):
    c0, c1 = p[0], p[1]
    b = p[2] if model == 'cross' else 0.0
    lnr = c0 - c1 * N - b * lnN          # ln(lambda * T)
    lnr = np.clip(lnr, -60, 40)
    pr = 1.0 - np.exp(-np.exp(lnr))
    pr = np.clip(pr, 1e-12, 1 - 1e-12)
    return -np.sum(nesc * np.log(pr) + (NT - nesc) * np.log(1 - pr))

def fit_model(model, seeds):
    best = None
    for s in seeds:
        res = minimize(negll, s, args=(model,), method='Nelder-Mead',
                       options=dict(maxiter=20000, xatol=1e-10, fatol=1e-10))
        if best is None or res.fun < best.fun:
            best = res
    return best

seeds = [[-3, 1e-3], [-3, 2e-3], [-3, 4e-3], [-2, 1e-3], [-4, 2e-3],
         [-3, 1e-3, 0.5], [-3, 2e-3, 1.0], [-2, 1e-3, 0.0], [-4, 4e-3, 1.5]]

print("\n" + "=" * 78)
print("(B) CENSORED BINOMIAL LIKELIHOOD ON ALL 8 POINTS  p = 1-exp(-lambda*T)")
print("=" * 78)
models = {}
for name, mdl, k in [("Kramers  ", 'kram', 2), ("Power    ", 'pow', 2),
                     ("Crossover", 'cross', 3)]:
    seeds_m = [s for s in seeds if (len(s) == 3) == (mdl == 'cross')]
    res = fit_model(mdl, seeds_m)
    AIC = 2*k + 2*res.fun
    models[name] = dict(negll=float(res.fun), AIC=float(AIC),
                        params=[float(x) for x in res.x], k=k)
    print(f"  {name}  negll={res.fun:9.4f}  AIC={AIC:9.4f}  params={np.round(res.x,6)}")

best = min(models.items(), key=lambda kv: kv[1]['AIC'])
print(f"\n  BEST BY AIC: {best[0].strip()}  (AIC={best[1]['AIC']:.3f})")
for nm in models:
    if nm != best[0]:
        print(f"    dAIC({nm.strip()} - {best[0].strip()}) = "
              f"{models[nm]['AIC'] - best[1]['AIC']:+.3f}")

# ---------------------------------------------- predicted escape counts vs observed
print("\n" + "=" * 78)
print("(C) POSTERIOR PREDICTIVE CHECK — expected escapes under each model")
print("=" * 78)
print(f"{'N':>6} {'obs':>5} | " + " | ".join(f"{nm.strip():>9}" for nm in models))
for i in range(n):
    row = f"{N[i]:>6.0f} {nesc[i]:>5.0f} | "
    cells = []
    for nm, m in models.items():
        p = m['params']
        b = p[2] if len(p) == 3 else 0.0
        lnr = p[0] - p[1]*N[i] - b*lnN[i]
        pr = 1 - np.exp(-np.exp(np.clip(lnr, -60, 40)))
        cells.append(f"{pr*NT:>9.2f}")
    print(row + " | ".join(cells))

out = dict(
    n_points=int(n), n_uncensored=int(unc.sum()),
    naive_6pt=dict(b=b_naive, c0=c0n, c1=c1n, rss_cross=rss_n, rss_kramers=rss_k_n),
    censored_likelihood=models, best_by_AIC=best[0].strip(),
)
json.dump(out, open("definitive_censoring.json", "w"), indent=1)
print("\nwrote definitive_censoring.json")
