"""Debug M37 CF vs MC."""
import numpy as np
from scipy.special import gamma, factorial
from itertools import product

def dirichlet_moment_cf(alpha, p):
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

# Debug K=2 alpha=(2,3) lam=(1,1)
alpha = (2.0, 3.0)
lam = (1.0, 1.0)
print(f"alpha={alpha}, lam={lam}")
print()
# First compute moments
for total_order in range(5):
    for p in product(range(total_order + 1), repeat=2):
        if sum(p) == total_order:
            moment = dirichlet_moment_cf(alpha, p)
            fact = np.prod([factorial(pi) for pi in p])
            coeff = moment / fact
            term = coeff * np.prod([(-lam[i])**p[i] for i in range(2)])
            print(f"  order {p}: E[X^p]={moment:.6f}, coeff={coeff:.6f}, term={term:.6f}")

print()
total = mgf_reconstruction_from_cf(alpha, lam, max_order=4)
print(f"Sum to order 4: {total:.6f}")
print(f"Expected: e^(-1) = {np.exp(-1):.6f}")
print(f"Note: for K=2 simplex, X1+X2=1 exactly, so exp(-lam·X) only depends on lam1-lam2.")
print(f"If lam=(1,1), then lam1-lam2=0, so exp(-lam·X)=exp(-1) regardless of X1 value.")
print(f"This is a CONSTANT for K=2 simplex, so Taylor series should converge to e^(-1).")
print()
# Add higher orders
for higher in range(5, 8):
    val = mgf_reconstruction_from_cf(alpha, lam, max_order=higher)
    print(f"  Sum to order {higher}: {val:.6f}")
