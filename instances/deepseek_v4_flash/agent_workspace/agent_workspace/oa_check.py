"""
OA self-consistency vs simulation for reflexive Kuramoto
dtheta = omega + K0*R^a*sin(psi - theta), omega ~ U(-1,1) (kappa=1)

Standard Kuramoto (a=0, coupling K0): partial sync state R = sqrt(1 - 2*kappa/K0), K0 > 2*kappa.
Reflexive: K_eff = K0*R^a. Self-consistency for uniform omega on [-kappa,kappa]:
    1 = (K0*R^a)/(2*kappa)  => R* = (2*kappa/K0)^(1/a)   (valid when R* < 1)
For (a=2, K0=5, kappa=1): R* = sqrt(0.4) = 0.632.

Question: does simulation lock to R* and does the escape-time law hold?
"""
import numpy as np

def sync_self_consistent(a, K0, kappa=1.0):
    cand = (2*kappa/K0)**(1.0/a)
    return cand if cand < 1.0 else None

print("=== OA self-consistency: R* = (2*kappa/K0)^(1/a) ===")
print(f"{'a':>4} {'K0':>4} {'R* (OA)':>10} {'R*<1?':>7}")
for a in [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
    for K0 in [5, 10, 15, 20]:
        R = sync_self_consistent(a, K0)
        print(f"{a:>4.1f} {K0:>4} {str(R):>10} {'YES' if R is not None else 'NO':>7}")