#!/usr/bin/env python3
"""Design calibration: where is the deterministic barrier R*?
dR/dt = (R/2)[K0 R^alpha (1-R^2) - sigma^2]
Barrier (unstable fixed point, ignoring 1-R^2 ~ 1):
  R* = (sigma^2 / K0)^(1/alpha)
Saddle-node (with 1-R^2): f(R) = K0 R^alpha (1-R^2) - sigma^2 = 0 has a solution
  iff max_R K0 R^alpha (1-R^2) >= sigma^2.
  max of R^alpha (1-R^2): R_m = sqrt(alpha/(alpha+2)), value = (alpha/(alpha+2))^(alpha/2) * 2/(alpha+2)
So K_sn = sigma^2 / [ (alpha/(alpha+2))^(alpha/2) * 2/(alpha+2) ].
"""
import numpy as np

def barrier(sigma, K0, alpha):
    if alpha == 0:
        # standard Kuramoto: f(R) = K0(1-R^2)/2 - sigma^2/2 -> stable at ~sqrt(1-2s2/K0)
        if K0 <= 2*sigma**2:
            return None, 0.0
        return None, np.sqrt(max(0.0, 1 - 2*sigma**2/K0))
    rstar = (sigma**2/K0)**(1/alpha)
    return rstar, None

def K_sn(sigma, alpha):
    if alpha == 0:
        return 2*sigma**2
    Rm = np.sqrt(alpha/(alpha+2))
    fmax = Rm**alpha * (1 - Rm**2)
    return sigma**2 / fmax

for sigma in [0.05, 0.1, 0.2, 0.5]:
    for alpha in [0.5, 1.0, 2.0]:
        for K0 in [1.0, 3.0, 10.0]:
            rstar, _ = barrier(sigma, K0, alpha)
            sn = K_sn(sigma, alpha)
            print(f"sigma={sigma:.2f} alpha={alpha:.1f} K0={K0:5.1f} | K_sn={sn:7.4f} "
                  f"| R*={rstar if rstar else 'n/a':>8} | belowK_sn={'YES' if K0<sn else 'no '}")
    print()

# key calibration question: for a barrier to exist with R0 below R*, what K range?
print("=== Example: sigma=0.2, alpha=1.0 ===")
sigma, alpha = 0.2, 1.0
sn = K_sn(sigma, alpha)
print(f"K_sn = {sn:.4f}")
for K0 in [sn*0.5, sn*0.6, sn*0.7, sn*0.8, sn*0.9, sn*0.95, sn*0.99, sn*1.01, sn*1.05]:
    rstar, _ = barrier(sigma, K0, alpha)
    print(f"  K0={K0:.4f} (delta={sn-K0:+.4f}) R*={rstar:.4f}  (R0 desired << {rstar:.4f})")