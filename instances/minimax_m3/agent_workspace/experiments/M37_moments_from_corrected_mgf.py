"""
M37: Deriving the classical Dirichlet moment formula from the corrected MGF.
Optimized version using cached log-gammas.
"""

import numpy as np
from scipy.special import gammaln
from math import comb
from functools import lru_cache


@lru_cache(maxsize=None)
def log_fact(n):
    return gammaln(n + 1)


def corrected_mgf_single(alpha_tuple, lam_tuple, N_max):
    """Single evaluation of corrected Dirichlet MGF."""
    alpha = np.asarray(alpha_tuple, dtype=float)
    lam = np.asarray(lam_tuple, dtype=float)
    K = len(alpha)
    alpha0 = alpha.sum()
    log_alpha0_g = gammaln(alpha0)
    total = 0.0
    for n in range(N_max + 1):
        def recurse(idx, remaining, vec):
            nonlocal total
            if idx == K - 1:
                m = vec + [remaining]
                log_mn = log_fact(n) - sum(log_fact(mi) for mi in m)
                log_poch = (gammaln(alpha0 + n) - log_alpha0_g)
                for i in range(K):
                    log_poch += (gammaln(alpha[i] + m[i]) - gammaln(alpha[i]))
                log_lam = sum(m[i] * np.log(abs(lam[i]) + 1e-30) for i in range(K))
                sign = (-1) ** n
                total += sign * np.exp(log_mn + log_poch + log_lam)
                return
            for j in range(remaining + 1):
                recurse(idx + 1, remaining - j, vec + [j])
        recurse(0, n, [])
    return total


def moment_numerical_diff(alpha, r, eps=1e-3, N_max=40):
    """E[prod_i X_i^{r_i}] via numerical differentiation of corrected MGF."""
    alpha = np.asarray(alpha, dtype=float)
    r = np.asarray(r, dtype=int)
    K = len(alpha)
    r0 = int(r.sum())
    total = 0.0

    def recurse(idx, vec, prod_C):
        nonlocal total
        if idx == K:
            lam_vec = tuple(eps * v for v in vec)
            mgf_val = corrected_mgf_single(tuple(alpha), lam_vec, N_max)
            total += prod_C * mgf_val
            return
        for j in range(r[idx] + 1):
            c = comb(r[idx], j) * ((-1) ** (r[idx] - j))
            recurse(idx + 1, vec + [j], prod_C * c)
    recurse(0, [], 1.0)
    return (-1) ** r0 * total / (eps ** r0)


def classical_moment(alpha, r):
    """E[prod_i X_i^{r_i}] via classical Dirichlet moment formula."""
    alpha = np.asarray(alpha, dtype=float)
    r = np.asarray(r, dtype=int)
    K = len(alpha)
    alpha0 = alpha.sum()
    r0 = int(r.sum())
    log_num = gammaln(alpha0) + sum(gammaln(alpha[i] + r[i])
                                    - gammaln(alpha[i]) for i in range(K))
    log_den = gammaln(alpha0 + r0)
    return np.exp(log_num - log_den)


def mc_moment(alpha, r, n_samples=2_000_000, seed=123):
    rng = np.random.default_rng(seed)
    samples = rng.dirichlet(alpha, size=n_samples)
    return np.mean(np.prod(samples ** r, axis=1))


# Tests across various alpha, r (only low-dim cases due to combinatorial explosion)
test_cases = [
    ([2.0, 3.0], [1, 2], "K=2, r=(1,2)"),
    ([2.0, 3.0], [3, 1], "K=2, r=(3,1)"),
    ([2.0, 3.0, 1.5], [1, 1, 1], "K=3, r=(1,1,1)"),
    ([5.0, 2.0, 0.5], [2, 1, 0], "K=3, r=(2,1,0)"),
    ([2.0, 2.0, 2.0, 2.0], [1, 1, 0, 1], "K=4, r=(1,1,0,1)"),
    ([1.0, 1.0, 1.0, 1.0, 1.0], [1, 1, 0, 0, 1], "K=5, r=(1,1,0,0,1)"),
]

print(f"{'Case':<30} {'Numerical diff':<16} {'Classical':<16} {'MC':<14} {'|nd-classical|':<16}")
print("-" * 92)
for alpha, r, name in test_cases:
    nd = moment_numerical_diff(alpha, r, eps=5e-3, N_max=30)
    cl = classical_moment(alpha, r)
    mc = mc_moment(alpha, r, n_samples=1_000_000)
    err = abs(nd - cl)
    print(f"{name:<30} {nd:<16.8f} {cl:<16.8f} {mc:<14.6f} {err:<16.2e}")
