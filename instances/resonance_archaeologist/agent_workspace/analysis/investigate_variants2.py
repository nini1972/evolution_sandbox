#!/usr/bin/env python3
"""
More investigation into the treaty's K0=4.0 values.
The treaty says alpha=0 gives R~0.99, but we get ~0.786.
Let me check if there's a different coupling convention or frequency distribution.
"""
import numpy as np

# Check standard Kuramoto R(K) with different conventions
def kuramoto_standard(N, K, gamma=1.0, dt=0.10, T_trans=40, T_meas=80, seed=0, freq_dist='cauchy'):
    np.random.seed(seed)
    if freq_dist == 'cauchy':
        omega = gamma * np.random.standard_cauchy(N)
    elif freq_dist == 'uniform':
        omega = gamma * (2 * np.random.rand(N) - 1)  # uniform [-1, 1]
    elif freq_dist == 'gaussian':
        omega = gamma * np.random.randn(N)
    theta = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta))
        theta += dt * (omega + K * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta))
        theta += dt * (omega + K * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas)

print("=== Standard Kuramoto R(K=4.0) with different frequency distributions ===")
for dist in ['cauchy', 'uniform', 'gaussian']:
    R_vals = []
    for seed in range(5):
        r = kuramoto_standard(200, 4.0, seed=seed, freq_dist=dist)
        R_vals.append(r)
    print(f"  {dist:10s}: R={np.mean(R_vals):.4f} +/- {np.std(R_vals):.4f} (seeds 0-4)")

# Check: what K would give R~0.99 with Cauchy?
print("\n=== What K gives R~0.99 with Cauchy? ===")
for K in np.linspace(2, 10, 17):
    R_vals = []
    for seed in range(2):
        r = kuramoto_standard(200, K, seed=seed, freq_dist='cauchy')
        R_vals.append(r)
    print(f"  K={K:.2f}: R={np.mean(R_vals):.4f}")

# Let's also try the R_eff model (self-consistent field approximation)
# In this model, R_ss = R_static(K0 * R_ss^alpha)
# For alpha=0: R_ss = R_static(K0) = R_static(4.0) ≈ 0.786
# This matches treaty's alpha=0 giving "R~0.99"? No, 0.786 ≠ 0.99

# What if the treaty uses a different definition of R?
# Or what if they use N->infinity (analytic solution)?
# For Cauchy with gamma=1, the analytic R satisfies:
# R = (K/2) * integral over g(omega) of R/sqrt((K*R)^2 + (omega)^2) ... 
# Actually, the self-consistency equation for Kuramoto with Cauchy(gamma):
# r = (K * r) / (2 * sqrt((K*r)^2 + gamma^2)) ... no
# The standard result: for K > K_c = 2*gamma, 
# r = sqrt(1 - (K_c/K)^2) for K > K_c (for Cauchy with half-width gamma)
# Wait, that's not right either. Let me recall...
# For Cauchy distribution g(omega) = gamma / (pi * (omega^2 + gamma^2)):
# The self-consistency equation is: r = K * r / (2*gamma) * ... 
# Actually: K_c = 2*gamma, and for K > K_c:
# r = 1 - sqrt(1 - (K_c/K)^2) ... no

# The exact solution: for K > K_c = 2*gamma:
# r = sqrt(1 - (K_c/K)^2) doesn't converge... let me just compute numerically
# The exact self-consistent equation for Cauchy:
# r = K * r * integral_{-inf}^{inf} g(omega) / (1 + (omega/(K*r))^2) d omega
# For Cauchy g(omega) = gamma/(pi*(omega^2+gamma^2)):
# This gives r = K*r/2 * 1/sqrt((K*r/2)^2 + gamma^2) * ... 

# Actually the known result is: for K > K_c = 2*gamma:
# r = 1 - gamma*sqrt(1/((K/2)^2 - gamma^2)) * ... 
# Let me just look at: the exact mean-field R for Cauchy
# r = sqrt(1 - K_c/K) for K > K_c? No...

# Let me just numerically solve the self-consistency equation
from scipy.integrate import quad
from scipy.optimize import brentq

gamma = 1.0
K_c = 2 * gamma  # = 2.0

def cauchy_r(k):
    """Exact mean-field R for Cauchy with half-width gamma, coupling k"""
    if k <= K_c:
        return 0.0
    # Self-consistency: r = k * r * integral g(omega) * 1/(1 + (omega/(k*r))^2) d omega
    # = k*r * <1/(1 + (omega/(k*r))^2)>
    # For Cauchy: integral = 1/(1 + k*r/gamma * ...) 
    # Actually the known result: r = 1 - sqrt(1 - (2*gamma/k)^2) ... let me check
    # The standard result is: k*r = gamma * cot(gamma * k * r / ...) 
    # Better: numerically solve r = k*r*integral
    def eq(r):
        if r < 1e-12:
            return 0
        def integrand(omega):
            g = gamma / (np.pi * (omega**2 + gamma**2))
            return g / (1 + (omega/(k*r))**2)
        val, _ = quad(integrand, -50, 50)
        return r - k * r * val
    try:
        r_sol = brentq(eq, 0.001, 0.999)
        return r_sol
    except:
        return None

print("\n=== Exact mean-field R(K) for Cauchy(gamma=1) ===")
for K in [0, 0.5, 1.0, 1.5, 1.9, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0]:
    r = cauchy_r(K)
    if r is not None:
        print(f"  K={K:.1f}: R_exact={r:.4f}")
    else:
        print(f"  K={K:.1f}: R_exact=0 (below K_c)")

# The treaty says at K0=4.0, alpha=0: R~0.99
# But exact mean-field gives R(4.0) ≈ 0.624 for Cauchy!
# And N=200 simulation gives ~0.786 (finite-size effects)
# So how does the treaty get R~0.99?

# What if they use gamma different, like gamma=0.5?
print("\n=== Exact mean-field R(K=4.0) for different gamma ===")
for gamma in [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
    Kc = 2*gamma
    def eq(r, k=4.0, g=gamma):
        if r < 1e-12:
            return -1
        def integrand(omega):
            gg = g / (np.pi * (omega**2 + g**2))
            return gg / (1 + (omega/(k*r))**2)
        val, _ = quad(integrand, -50, 50)
        return r - k * r * val
    try:
        r_sol = brentq(eq, 0.001, 0.999)
        print(f"  gamma={gamma:.2f}, K_c={Kc:.2f}: R(4.0)={r_sol:.4f}")
    except:
        print(f"  gamma={gamma:.2f}, K_c={Kc:.2f}: R(4.0)=0 (below K_c)")
