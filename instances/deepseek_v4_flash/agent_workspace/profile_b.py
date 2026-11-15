#!/usr/bin/env python3
"""
profile_b.py — is the crossover's b=0 a bound artifact or a genuine degeneracy?

Two questions:
 (1) Profile the RSS over FIXED b (fit c0,c1 only at each b) — if RSS is flat
     or monotonically increasing in b, the log term is genuinely unsupported
     by 6 aggregate points.
 (2) Likelihood-ratio test on the binomial (censored-count) likelihood:
     H0: b=0 (Kramers, 2 params) vs H1: b free (crossover, 3 params).
     Also test the properly censored form p = 1 - exp(-lambda*T).
"""
import json
import numpy as np
from scipy.optimize import curve_fit, minimize_scalar
from scipy.stats import chi2

N     = np.array([40, 80, 160, 320, 640, 1280], float)
esc   = np.array([256, 256, 254, 186, 55, 4], float)
total = np.array([256, 256, 256, 256, 256, 256], float)
lnN   = np.log(N)
lam   = esc / total
lnlam = np.log(lam)
n     = len(N)

# ---------------- (1) RSS profile over fixed b ----------------
def rss_at_b(b):
    # ln_lam = c0 - c1*N - b*lnN  ->  fit linear in (c0,c1) by lstsq
    A = np.column_stack([np.ones(n), -N])
    y = lnlam + b * lnN
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    return float(np.sum(r**2)), coef

bs = np.linspace(-0.5, 2.5, 121)
prof = [(b, *rss_at_b(b)[0:1]) for b in bs]
rss_free, coef_free = rss_at_b(0.0)
b_best = bs[int(np.argmin([p[1] for p in prof]))]
rss_best = min(p[1] for p in prof)

# refine
def obj(b):
    return rss_at_b(b)[0]
res = minimize_scalar(obj, bounds=(-1.0, 3.0), method='bounded')
b_opt, rss_opt = float(res.x), float(res.fun)

# ---------------- (2) censored binomial likelihoods ----------------
# horizon T: escape times exponential with rate lambda -> p = 1 - exp(-lambda*T)
# We do not know T, so absorb lambda*T into a single rate r = lambda*T and fit
# ln r = c0 - c1*N - b*lnN.  This is a RESCALING of the same law, so model
# comparison is unchanged, but the likelihood is a proper censored one.
def negll(params, form):
    c0, c1 = params[0], params[1]
    b = params[2] if form == 'cross' else 0.0
    lnr = c0 - c1 * N - b * lnN
    lnr = np.clip(lnr, -50, 50)
    p = 1.0 - np.exp(-np.exp(lnr))
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -np.sum(esc * np.log(p) + (total - esc) * np.log(1 - p))

# H0: Kramers
r0 = minimize_scalar(lambda c1: negll([0.0, c1], 'kram'), bounds=(-1e-3, 1e-2),
                     method='bounded')
best0 = None
for c0g in np.linspace(-5, 5, 21):
    for c1g in np.linspace(0, 8e-3, 17):
        v = negll([c0g, c1g], 'kram')
        if best0 is None or v < best0[0]:
            best0 = (v, c0g, c1g)
ll0 = -best0[0]

# H1: crossover
best1 = None
for c0g in np.linspace(-5, 5, 11):
    for c1g in np.linspace(0, 8e-3, 9):
        for bg in np.linspace(-0.5, 2.0, 11):
            v = negll([c0g, c1g, bg], 'cross')
            if best1 is None or v < best1[0]:
                best1 = (v, c0g, c1g, bg)
ll1 = -best1[0]

lr = 2 * (ll1 - ll0)
pval = float(chi2.sf(max(lr, 0), df=1))

out = dict(
    rss_profile=dict(b_opt=b_opt, rss_opt=rss_opt, rss_at_b0=rss_free,
                     delta_rss=rss_free - rss_opt,
                     note="delta_rss>0 means a log term helps; ~0 means it does not"),
    censored_likelihood=dict(
        H0_kramers=dict(negll=float(best0[0]), c0=float(best0[1]), c1=float(best0[2])),
        H1_crossover=dict(negll=float(best1[0]), c0=float(best1[1]),
                          c1=float(best1[2]), b=float(best1[3])),
        LR=float(lr), p_value=pval, AIC0=float(2*2+2*best0[0]),
        AIC1=float(2*3+2*best1[0]),
        delta_AIC=float((2*2+2*best0[0]) - (2*3+2*best1[0])),
    ),
)
json.dump(out, open("profile_b.json", "w"), indent=1)

print("=" * 66)
print("RSS PROFILE OVER b   (crossover = kramers + b*lnN)")
print("=" * 66)
print(f"  b_opt = {b_opt:+.4f}   RSS(b_opt) = {rss_opt:.6f}")
print(f"  RSS(b=0)          = {rss_free:.6f}")
print(f"  delta RSS (b=0 minus b_opt) = {rss_free - rss_opt:+.6f}")
print("  => log term helps by %s" % ("a real amount" if rss_free - rss_opt > 1e-3 else "essentially nothing"))
print()
print("=" * 66)
print("CENSORED BINOMIAL LIKELIHOOD  p = 1 - exp(-exp(ln r))")
print("=" * 66)
print(f"  H0 Kramers   negll={best0[0]:9.3f}  c0={best0[1]:+.4f} c1={best0[2]:.5f}  AIC={2*2+2*best0[0]:.2f}")
print(f"  H1 Crossover negll={best1[0]:9.3f}  c0={best1[1]:+.4f} c1={best1[2]:.5f} b={best1[3]:+.4f}  AIC={2*3+2*best1[0]:.2f}")
print(f"  LR = {lr:.3f}  p = {pval:.4f}   delta_AIC(H0-H1) = {out['censored_likelihood']['delta_AIC']:+.2f}")
print("  => %s" % ("crossover supported" if pval < 0.05 else "crossover NOT supported at 6 points"))
print()
print("wrote profile_b.json")
