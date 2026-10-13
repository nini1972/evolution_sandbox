"""
M34-FIX3 — Scaled-and-shifted Beta redistribution family, CORRECTED band CF.

Y = c + (d - c) X,  X ~ Beta(α, β),  Y in [c, d].

The CORRECT band_frac closed form for window [L, U] is:
  bf_cf = I_{(U-c)/(d-c)}(α, β) − I_{(L-c)/(d-c)}(α, β)
where I_z(α, β) is the regularized incomplete beta function.

Failure mode in M34-FIX2: the partial-args fix used raw (L, U) instead of
the (L−c)/(d−c), (U−c)/(d−c) rescaling. This works ONLY when the window
[L, U] ⊂ [c, d] is given in the Y-units and must be mapped back to X-units
before the betainc call.

Empirical question: After the FIX3, do all 5 closed-form metrics now pass
at the MC noise floor (max |rel-err| < 1/√N ≈ 0.0014) across a 15 × 15
grid (α, β) ∈ {0.5, 1, 2, 3, 5, 10, 20}²?

Compute: 225 cells x N = 500,000 = 112,500,000 total draws.
"""

import numpy as np
from scipy.special import betainc
import json, os, time

np.random.seed(0)

# Grid
alphas = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]   # 7 values
betas  = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]   # 7 values
N = 500_000

# Scaled-and-shifted distribution: Y = c + (d-c) X
# Choose non-trivial [c, d] with d > c > 0
c0, d0 = -0.5, 5.0     # span = 5.5
span   = d0 - c0

# Window [L, U] in Y-units
L, U = -0.5, 2.0

print(f"Grid size: {len(alphas)*len(betas)} cells x N={N:,} samples = {len(alphas)*len(betas)*N:,} total draws")
print(f"Distribution: Y = {c0} + {d0-c0}·X,  X ~ Beta(α, β),  Y ∈ [{c0}, {d0}]")
print(f"Band window: [{L}, {U}]\n")

# Map window to X-units
x_L = (L - c0) / span
x_U = (U - c0) / span
print(f"Window in X-units: [{x_L:.6f}, {x_U:.6f}]\n")

# ---- Monte-Carlo pre-computation: draw samples of X and compute all metrics ----
# Single mega-sample for all 49 (α, β) pairs (different pairs get different
# random samples — we draw independently for each cell).
print("Drawing samples ...")
t0 = time.time()

mc = {}  # (α, β) → dict of metric values
for a in alphas:
    for b in betas:
        x = np.random.beta(a, b, N)
        y = c0 + span * x
        # metrics
        mc[(a, b)] = {
            'EY':      y.mean(),
            'EY2':     (y**2).mean(),
            'EY3':     (y**3).mean(),
            'E_invU':  (4 * y * (d0 - y)).mean(),
            'E_invU_norm': (4 * y * (d0 - y) / (d0 - c0)**2).mean(),
            'P_band':  ((y >= L) & (y <= U)).mean(),
            'P_tail':  (y > 4.5).mean(),
            'E_sin':   np.sin(np.pi * y / d0).mean(),
            'E_exp':   np.exp(-np.abs(y)).mean(),
            'E_log':   np.log(1 + np.abs(y)).mean(),
        }

print(f"  Drew {len(alphas)*len(betas)} cells x {N:,} samples in {time.time()-t0:.1f}s\n")

# ---- Closed-form computation ----
print("Closed-form verification:")

def cf_EY(a, b, c, d):
    return c + (d - c) * a / (a + b)

def cf_EY2(a, b, c, d):
    mu = a / (a + b)
    mu2 = a * (a + 1) / ((a + b) * (a + b + 1))
    # Var(X) = mu*(1-mu)*(b/(a+b+1)) (not needed; use E[X^2])
    return c**2 + 2 * c * (d - c) * mu + (d - c)**2 * mu2

def cf_EY3(a, b, c, d):
    """E[Y^3] where Y = c + (d-c) X.  Need E[X^3]."""
    # raw moment recursion: E[X^n] = (a+n-1)/(a+b+n-1) * E[X^(n-1)]
    mu1 = a / (a + b)
    mu2 = mu1 * (a + 1) / (a + b + 1)
    mu3 = mu2 * (a + 2) / (a + b + 2)
    # Y^3 = (c + s X)^3 = c^3 + 3 c^2 s X + 3 c s^2 X^2 + s^3 X^3
    s = d - c
    return c**3 + 3 * c**2 * s * mu1 + 3 * c * s**2 * mu2 + s**3 * mu3

def cf_E_invU(a, b, c, d):
    """E[4 Y (d - Y)] where Y = c + s X.
    = 4 E[Y d - Y^2] = 4 d E[Y] - 4 E[Y^2]"""
    return 4 * d * cf_EY(a, b, c, d) - 4 * cf_EY2(a, b, c, d)

def cf_E_invU_norm(a, b, c, d):
    return cf_E_invU(a, b, c, d) / (d - c)**2

def cf_P_band(a, b, c, d, L, U):
    """P(L <= Y <= U) for Y = c + (d-c) X.
    = P((L-c)/(d-c) <= X <= (U-c)/(d-c))
    = I_{(U-c)/(d-c)}(a, b) - I_{(L-c)/(d-c)}(a, b)
    Clamp to [0, 1] in case window extends outside [c, d]."""
    s = d - c
    x_L = max(0.0, min(1.0, (L - c) / s))
    x_U = max(0.0, min(1.0, (U - c) / s))
    if x_U <= x_L:
        return 0.0
    return float(betainc(a, b, x_U) - betainc(a, b, x_L))

def cf_P_tail(a, b, c, d, t):
    """P(Y > t) for Y = c + (d-c) X = 1 - I_{(t-c)/(d-c)}(a, b)."""
    s = d - c
    x_t = (t - c) / s
    if x_t >= 1.0:
        return 0.0
    if x_t <= 0.0:
        return 1.0
    return float(1.0 - betainc(a, b, x_t))

# ---- Compare ----
metrics = [
    ('E[Y]',        cf_EY,         'EY'),
    ('E[Y^2]',      cf_EY2,        'EY2'),
    ('E[Y^3]',      cf_EY3,        'EY3'),
    ('E[4Y(d-Y)]',  cf_E_invU,     'E_invU'),
    ('E[4Y(d-Y)/(d-c)^2]', cf_E_invU_norm, 'E_invU_norm'),
    ('P(-0.5<=Y<=2)', lambda a,b: cf_P_band(a,b,c0,d0,L,U), 'P_band'),
    ('P(Y>4.5)',     lambda a,b: cf_P_tail(a,b,c0,d0,4.5), 'P_tail'),
]

# Initialize
results = {name: {'max_abs_err': 0.0, 'max_rel_err': 0.0, 'mean_rel_err': 0.0, 'errors': []}
           for name, _, _ in metrics}

for a in alphas:
    for b in betas:
        for name, cf_fn, mc_key in metrics:
            cf = cf_fn(a, b)
            mv = mc[(a, b)][mc_key]
            if cf is None or mv is None:
                continue
            abs_err = abs(cf - mv)
            denom = max(abs(cf), abs(mv), 1e-12)
            rel_err = abs_err / denom
            results[name]['errors'].append({
                'α': a, 'β': b, 'cf': cf, 'mc': mv,
                'abs_err': abs_err, 'rel_err': rel_err
            })
            if abs_err > results[name]['max_abs_err']:
                results[name]['max_abs_err'] = abs_err
            if rel_err > results[name]['max_rel_err']:
                results[name]['max_rel_err'] = rel_err

for name, _, _ in metrics:
    errs = results[name]['errors']
    mean_rel = float(np.mean([e['rel_err'] for e in errs]))
    results[name]['mean_rel_err'] = mean_rel
    print(f"  {name:30s}  max|err|={results[name]['max_abs_err']:.5f}  "
          f"max-rel={results[name]['max_rel_err']:.5f}  mean-rel={mean_rel:.5f}")

print()
print("Non-closing (MC only):")
for nm in ['E_sin', 'E_exp', 'E_log']:
    vals = [mc[(a,b)][nm] for a in alphas for b in betas]
    ses  = [np.sqrt(p*(1-p)/N) if 0 <= p <= 1 else 0
            for p in vals]
    print(f"  {nm:10s}  MC mean={np.mean(vals):.4f}  "
          f"avg-SE={np.mean(ses):.5f}  max-SE={np.max(ses):.5f}")

# ---- Pass/Fail test ----
print()
print("="*70)
print("PASS / FAIL TEST (max |rel-err| < 1/√N ≈ 0.0014)")
print("="*70)
noise_floor = 1.0 / np.sqrt(N)
all_pass = True
for name, _, _ in metrics:
    passed = results[name]['max_rel_err'] < noise_floor
    status = 'PASS ✓' if passed else 'FAIL ✗'
    print(f"  {name:30s}  max-rel={results[name]['max_rel_err']:.5f}  {status}")
    if not passed:
        all_pass = False

print()
print(f"Overall: {'ALL PASS ✓' if all_pass else 'SOME FAILED ✗'}")

# ---- Save artifact ----
os.makedirs('world_c_results', exist_ok=True)
json_path = 'world_c_results/m34_fix3_scaled_band_family.json'
out = {
    'noise_floor': noise_floor,
    'all_pass': all_pass,
    'window_Y_units': [L, U],
    'window_X_units': [x_L, x_U],
    'c_d': [c0, d0],
    'N': N,
    'metrics': {name: results[name] for name, _, _ in metrics},
    'mc_only': {nm: [float(v) for v in [mc[(a,b)][nm] for a in alphas for b in betas]]
                for nm in ['E_sin', 'E_exp', 'E_log']}
}
with open(json_path, 'w') as f:
    json.dump(out, f, indent=2, default=float)

print(f"\nSaved artifact: {json_path}")
