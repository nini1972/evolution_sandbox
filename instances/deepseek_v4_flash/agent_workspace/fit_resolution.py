#!/usr/bin/env python3
"""
fit_resolution.py — resolve the contradiction between my two artifacts.

km_barrier_corrected.json  -> verdict "KRAMERS"
crossover_model.json       -> verdict "CROSSOVER"

Suspicion: the "corrected" fitter has a SIGN CONVENTION bug
(form  ln_lam = c0 - c1*N  reported with c1 = -0.0055, which makes the
rate INCREASE with N — impossible for an escape rate).  I recompute
everything from the 6 usable log-rates with explicit, checked signs and
report an honest, reproducible verdict.

Data: 6 usable N values (N=2560,5120 are 100% censored -> excluded, as they
carry no rate information). 256 trajectories per N.
"""
import json, itertools
import numpy as np
from scipy.optimize import curve_fit

# ---- observed data (from km_barrier_corrected.json rows) ----
N      = np.array([40, 80, 160, 320, 640, 1280], float)
esc    = np.array([256, 256, 254, 186, 55, 4], float)          # escaped count
total  = np.array([256, 256, 256, 256, 256, 256], float)       # trajectories
lam    = esc / total                                            # MLE-ish rate
lnlam  = np.log(lam)
lnN    = np.log(N)

# ---- the four rival laws (ln rate as a function of N) ----
def f_kramers(N, c0, c1):      return c0 - c1 * N            # 2 params
def f_power(N, c0, b):         return c0 - b * np.log(N)      # 2 params
def f_crossover(N, c0, c1, b): return c0 - c1 * N - b * np.log(N)  # 3 params
def f_horizon(N, c0):          return c0 - 0.5 * np.log(N)    # 1 param (b=0.5 fixed)

MODELS = {
    "kramers":   (f_kramers,   2, [(-10, 1), (-1e-4, 1e-2)]),
    "power":     (f_power,     2, [(-10, 20), (0, 5)]),
    "crossover": (f_crossover, 3, [(-10, 20), (-1e-4, 1e-2), (0, 5)]),
    "horizon":   (f_horizon,   1, [(-10, 20)]),
}

n = len(N)
results = {}
for name, (fn, k, bounds) in MODELS.items():
    try:
        if name == "horizon":
            p = np.array([np.mean(lnlam + 0.5 * lnN)])
        else:
            p, _ = curve_fit(fn, N, lnlam, p0=[-3.0, 0.003, 0.9][:k],
                             bounds=tuple(zip(*bounds)), maxfev=200000)
        pred = fn(N, *p)
        res  = lnlam - pred
        rss  = float(np.sum(res**2))
        rms  = float(np.sqrt(rss / n))
        r2   = 1 - rss / np.sum((lnlam - lnlam.mean())**2)
        # RSS-based AIC (Gaussian, sigma profiled): n*ln(rss/n) + 2k
        aic  = n * np.log(max(rss, 1e-12) / n) + 2 * k
        results[name] = dict(params=[float(x) for x in p], k=k, rss=rss,
                             rms=rms, r2=float(r2), aic=float(aic),
                             pred=[float(x) for x in pred],
                             resid=[float(x) for x in res])
    except Exception as e:
        results[name] = dict(error=str(e))

# ---- per-trajectory binomial AIC (uses counts, not just log-rates) ----
# treat each N as Binomial(total, p_i) with p_i = exp(ln_lam_pred) clipped
def binom_ll(pred_ln):
    p = np.clip(np.exp(pred_ln), 1e-12, 1 - 1e-12)
    return float(np.sum(esc * np.log(p) + (total - esc) * np.log(1 - p)))
for name in results:
    if "pred" in results[name]:
        ll = binom_ll(np.array(results[name]["pred"]))
        results[name]["binom_ll"] = ll
        results[name]["binom_aic"] = -2 * ll + 2 * results[name]["k"]

best_rss   = min(results, key=lambda m: results[m]["aic"])
best_binom = min(results, key=lambda m: results[m].get("binom_aic", 1e9))

# ---- leverage bootstrap: resample the 6 points WITH replacement ----
rng = np.random.default_rng(20241114)
wins = {m: 0 for m in MODELS}
b_samples = []
reps = 2000
for _ in range(reps):
    idx = rng.integers(0, n, n)
    Ns, ys = N[idx], lnlam[idx]
    aics = {}
    for name, (fn, k, bounds) in MODELS.items():
        try:
            if name == "horizon":
                p = np.array([np.mean(ys + 0.5 * np.log(Ns))])
            else:
                p, _ = curve_fit(fn, Ns, ys, p0=[-3.0, 0.003, 0.9][:k],
                                 bounds=tuple(zip(*bounds)), maxfev=200000)
            rss = float(np.sum((ys - fn(Ns, *p))**2))
            aics[name] = n * np.log(max(rss, 1e-12) / n) + 2 * k
            if name == "crossover":
                b_samples.append(float(p[2]))
        except Exception:
            aics[name] = 1e9
    wins[min(aics, key=aics.get)] += 1

# ---- parametric bootstrap: generate data under CROSSOVER truth ----
p_cross = np.array(results["crossover"]["params"])
c0, c1, b = p_cross
mu = f_crossover(N, c0, c1, b)
sigma = results["crossover"]["rms"]
wins_par = {m: 0 for m in MODELS}
b_par = []
for _ in range(reps):
    ys = mu + rng.normal(0, sigma, n)
    aics = {}
    for name, (fn, k, bounds) in MODELS.items():
        try:
            if name == "horizon":
                p = np.array([np.mean(ys + 0.5 * np.log(N))])
            else:
                p, _ = curve_fit(fn, N, ys, p0=[-3.0, 0.003, 0.9][:k],
                                 bounds=tuple(zip(*bounds)), maxfev=200000)
            rss = float(np.sum((ys - fn(N, *p))**2))
            aics[name] = n * np.log(max(rss, 1e-12) / n) + 2 * k
            if name == "crossover":
                b_par.append(float(p[2]))
        except Exception:
            aics[name] = 1e9
    wins_par[min(aics, key=aics.get)] += 1

b_samples = np.array(b_samples); b_par = np.array(b_par)
out = dict(
    n_points=n, Ns=N.tolist(), rates=lam.tolist(), ln_rates=lnlam.tolist(),
    fits=results,
    best_by_rss_aic=best_rss,
    best_by_binom_aic=best_binom,
    delta_aic_crossover_vs_kramers=results["kramers"]["aic"] - results["crossover"]["aic"],
    leverage_bootstrap_wins=wins,
    crossover_b_median=float(np.median(b_samples)),
    crossover_b_ci95=[float(np.percentile(b_samples, 2.5)), float(np.percentile(b_samples, 97.5))],
    parametric_bootstrap_wins=wins_par,
    parametric_b_median=float(np.median(b_par)),
    parametric_b_ci95=[float(np.percentile(b_par, 2.5)), float(np.percentile(b_par, 97.5))],
    sign_check=dict(
        kramers_slope_must_be_negative=bool(results["kramers"]["params"][1] > 0),
        note="form c0 - c1*N with c1>0 => rate decreases with N (physical)"
    ),
)
json.dump(out, open("resolution_verdict.json", "w"), indent=1)

# ---- console report ----
print("=" * 68)
print("FIT RESOLUTION — 6 usable N points, 256 trajectories each")
print("=" * 68)
print(f"{'model':<11}{'k':>2}{'RMS':>10}{'R2':>10}{'AIC_rss':>11}{'AIC_binom':>11}")
for m in ["horizon", "kramers", "power", "crossover"]:
    r = results[m]
    print(f"{m:<11}{r['k']:>2}{r['rms']:>10.4f}{r['r2']:>10.5f}"
          f"{r['aic']:>11.2f}{r.get('binom_aic', float('nan')):>11.2f}")
print()
print("best by RSS-AIC   :", best_rss)
print("best by BINOM-AIC :", best_binom)
print("delta AIC (kramers - crossover) =", round(out['delta_aic_crossover_vs_kramers'], 2))
print()
print("crossover params  : c0=%.4f  c1=%.6f  b=%.4f" % (c0, c1, b))
print("leverage bootstrap wins :", wins)
print("  b median = %.4f  95%% CI = [%.4f, %.4f]" % (np.median(b_samples), *np.percentile(b_samples, [2.5, 97.5])))
print("parametric bootstrap wins:", wins_par)
print("  b median = %.4f  95%% CI = [%.4f, %.4f]" % (np.median(b_par), *np.percentile(b_par, [2.5, 97.5])))
print()
print("sign check (kramers rate decreasing with N):", out["sign_check"]["kramers_slope_must_be_negative"])
print("wrote resolution_verdict.json")
