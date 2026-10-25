"""
M37 v2: Closed-form Taylor reconstruction of Dirichlet MGF vs Monte Carlo.
Use non-degenerate lambda values (lambda_i sum != 1) so the K=2 simplex
constraint X1+X2=1 doesn't make exp(-lam·X) constant.
"""
import numpy as np
from scipy.special import gamma, factorial
from itertools import product
import json

def dirichlet_moment_cf(alpha, p):
    alpha0 = sum(alpha)
    P = sum(p)
    num = gamma(alpha0)
    den = gamma(alpha0 + P)
    prod = 1.0
    for ai, pi in zip(alpha, p):
        prod *= gamma(ai + pi) / gamma(ai) if pi > 0 else 1.0
    return (num / den) * prod

def mgf_reconstruction_from_cf(alpha, lam, max_order=6):
    K = len(alpha)
    total = 0.0
    terms_used = 0
    for total_order in range(max_order + 1):
        for p in product(range(total_order + 1), repeat=K):
            if sum(p) == total_order:
                moment = dirichlet_moment_cf(alpha, p)
                fact = np.prod([factorial(pi) for pi in p])
                coeff = moment / fact
                term = coeff * np.prod([(-lam[i])**p[i] for i in range(K)])
                total += term
                terms_used += 1
    return total, terms_used

def mgf_monte_carlo(alpha, lam, N=2_000_000, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    K = len(alpha)
    gammas = np.zeros((K, N))
    for i, ai in enumerate(alpha):
        gammas[i] = rng.gamma(ai, 1.0, N)
    X = gammas / gammas.sum(axis=0)
    t = np.exp(-np.dot(lam, X))
    return t.mean(), t.std() / np.sqrt(N)

# Test configurations: use lambda values with non-trivial structure
# K=2: avoid lam1=lam2; use lam=(0.7, 0.3) instead
configs = [
    (2, (2.0, 3.0), (0.7, 0.3), 6),       # alpha0=5
    (2, (0.5, 0.5), (0.6, 0.4), 6),        # uniform-like, but lam sum=1 so still degenerate
    (2, (0.5, 0.5), (0.8, 0.3), 6),        # non-degenerate
    (3, (1.0, 1.0, 1.0), (0.5, 0.4, 0.3), 6),  # uniform simplex, non-degenerate
    (3, (2.0, 3.0, 5.0), (0.5, 1.0, 1.5), 6),
    (4, (1.0, 1.0, 1.0, 1.0), (0.5, 0.4, 0.3, 0.2), 6),
    (4, (0.5, 1.0, 2.0, 3.0), (0.6, 0.5, 0.4, 0.3), 6),
    (5, (2.0, 2.0, 2.0, 2.0, 2.0), (0.4,)*5, 6),
    (6, (1.0,)*6, (0.4, 0.3, 0.3, 0.2, 0.2, 0.1), 5),
]

results = []
rng = np.random.default_rng(42)
print(f"{'K':<3} {'alpha':<35} {'lambda':<25} {'order':<6} {'CF':<12} {'MC':<12} {'abs_err':<12} {'MC_SE':<10}")
print("-" * 120)
max_err = 0
max_rel_err = 0
for K, alpha, lam, order in configs:
    cf_val, terms = mgf_reconstruction_from_cf(alpha, lam, max_order=order)
    mc_val, mc_se = mgf_monte_carlo(alpha, lam, N=2_000_000, rng=rng)
    abs_err = abs(cf_val - mc_val)
    rel_err = abs_err / max(abs(cf_val), 1e-10)
    max_err = max(max_err, abs_err)
    max_rel_err = max(max_rel_err, rel_err)
    alpha_s = str(tuple(round(a,2) for a in alpha))[:35]
    lam_s = str(tuple(round(l,2) for l in lam))[:25]
    print(f"{K:<3} {alpha_s:<35} {lam_s:<25} {order:<6} {cf_val:<12.6f} {mc_val:<12.6f} {abs_err:<12.2e} {mc_se:<10.2e}")
    results.append({
        'K': K, 'alpha': list(alpha), 'lambda': list(lam), 'order': order,
        'cf_value': float(cf_val), 'mc_value': float(mc_val),
        'abs_err': float(abs_err), 'rel_err': float(rel_err), 'mc_se': float(mc_se)
    })

print()
print(f"Max absolute error: {max_err:.2e}")
print(f"Max relative error: {max_rel_err:.2e}")
print(f"Noise floor (1/sqrt(2e6)) = {1/np.sqrt(2e6):.2e}")
print(f"All within noise floor (3x): {max_err < 3e-3}")

with open('m37_recovery_v2_results.json', 'w') as f:
    json.dump({'max_abs_err': max_err, 'max_rel_err': max_rel_err, 'configs': results}, f, indent=2)
print("\nSaved m37_recovery_v2_results.json")
