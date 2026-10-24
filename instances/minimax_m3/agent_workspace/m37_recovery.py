"""
M37: Verify that the multivariate Dirichlet MGF Taylor expansion
matches Monte Carlo to noise floor across K=2,3,4,5,6 configurations.

This is the "classical moment recovery" closure test for the M-series.
"""
import numpy as np
from scipy.special import gamma, factorial
from itertools import product
import json

def dirichlet_moment_cf(alpha, p):
    """Classical Dirichlet moment formula E[X^p] = (Gamma(a0)/Gamma(a0+P)) prod Gamma(ai+pi)/Gamma(ai)."""
    alpha0 = sum(alpha)
    P = sum(p)
    num = gamma(alpha0)
    den = gamma(alpha0 + P)
    prod = 1.0
    for ai, pi in zip(alpha, p):
        if pi == 0:
            prod *= 1.0
        else:
            prod *= gamma(ai + pi) / gamma(ai)
    return (num / den) * prod

def mgf_reconstruction_from_cf(alpha, lam, max_order=4):
    """Reconstruct E[exp(-lam·X)] = sum_p coeff_p * (-lam)^p where coeff_p = E[X^p]/p!."""
    K = len(alpha)
    total = 0.0
    for total_order in range(max_order + 1):
        for p in product(range(total_order + 1), repeat=K):
            if sum(p) == total_order:
                moment = dirichlet_moment_cf(alpha, p)
                fact = np.prod([factorial(pi) for pi in p])
                coeff = moment / fact
                term = coeff * np.prod([(-lam[i])**p[i] for i in range(K)])
                total += term
    return total

def mgf_monte_carlo(alpha, lam, N=1_000_000, rng=None):
    """Monte Carlo estimate of E[exp(-lam·X)] where X ~ Dir(alpha)."""
    if rng is None:
        rng = np.random.default_rng(42)
    K = len(alpha)
    # Sample Dirichlet via Gamma / sum
    gammas = np.zeros((K, N))
    for i, ai in enumerate(alpha):
        gammas[i] = rng.gamma(ai, 1.0, N)
    X = gammas / gammas.sum(axis=0)
    # Compute exp(-lam · X)
    t = np.exp(-np.dot(lam, X))
    return t.mean(), t.std() / np.sqrt(N)

# Test configurations
configs = [
    (2, (2.0, 3.0), (1.0, 1.0)),
    (2, (0.5, 0.5), (2.0, 2.0)),
    (3, (1.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    (3, (2.0, 3.0, 5.0), (0.5, 1.0, 1.5)),
    (4, (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)),
    (4, (0.5, 1.0, 2.0, 3.0), (1.0, 1.0, 1.0, 1.0)),
    (5, (2.0, 2.0, 2.0, 2.0, 2.0), (0.5, 0.5, 0.5, 0.5, 0.5)),
    (6, (1.0, 1.0, 1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)),
]

results = []
rng = np.random.default_rng(42)
print(f"{'K':<3} {'alpha':<30} {'lambda':<25} {'CF':<12} {'MC':<12} {'abs_err':<12} {'MC_SE':<10}")
print("-" * 110)
max_err = 0
for K, alpha, lam in configs:
    cf_val = mgf_reconstruction_from_cf(alpha, lam, max_order=4)
    mc_val, mc_se = mgf_monte_carlo(alpha, lam, N=1_000_000, rng=rng)
    abs_err = abs(cf_val - mc_val)
    max_err = max(max_err, abs_err)
    alpha_s = str(alpha)[:30]
    lam_s = str(lam)[:25]
    print(f"{K:<3} {alpha_s:<30} {lam_s:<25} {cf_val:<12.6f} {mc_val:<12.6f} {abs_err:<12.2e} {mc_se:<10.2e}")
    results.append({
        'K': K, 'alpha': alpha, 'lambda': lam,
        'cf_value': cf_val, 'mc_value': mc_val,
        'abs_err': abs_err, 'mc_se': mc_se,
        'noise_floor': 1e-3  # 1/sqrt(N)
    })

print()
print(f"Max absolute error across {len(configs)} configurations: {max_err:.2e}")
print(f"Noise floor (1/sqrt(N=10^6)) = 1.00e-03")
print(f"All within noise floor: {max_err < 1e-3}")

# Save artifacts
with open('m37_recovery_results.json', 'w') as f:
    json.dump({'max_err': max_err, 'configs': results}, f, indent=2, default=str)
print("\nSaved m37_recovery_results.json")
