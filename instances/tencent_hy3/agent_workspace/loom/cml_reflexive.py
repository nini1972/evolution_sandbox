"""Test the Meta-Law of Bootstrapability on a DIFFERENT family:
a Coupled-Map Lattice / mean-field circle-map with reflexive coupling
K = K0 * R**alpha. Local dynamics = Bernoulli circle map (chaotic),
so this is structurally different from the sine-Rössler Kuramoto flow.

Prediction (universal): for alpha>1 the order cannot bootstrap from disorder
(R stays low at large K0); for alpha<1 it locks. If true, the law is
dynamics-independent, not a Kuramoto artifact."""
import numpy as np, time

def simulate(alpha, K0, eps=2.0, N=150, T=400, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, N)
    for _ in range(T):
        e = np.exp(1j*theta); z = np.mean(e); R = abs(z); phi = np.angle(z)
        K = K0*(R**alpha) if R > 0 else 0.0
        # local Bernoulli circle map + mean-field pull
        theta = (2.0*theta) % (2*np.pi) + eps*K*np.sin(phi - theta)
        theta = theta % (2*np.pi)
    e = np.exp(1j*theta); return abs(np.mean(e))

def mean_R(a,K0,seeds=2):
    return float(np.mean([simulate(a,K0,seed=s) for s in range(seeds)]))

t0=time.time()
print("CML reflexive: alpha sweep at fixed K0 (random init)")
for K0 in [3.0, 6.0]:
    print(f"=== K0={K0} ===")
    print("  ".join(f"a{a}:R={mean_R(a,K0):.2f}" for a in [0.5,1.0,1.5]))
print("elapsed", round(time.time()-t0,1))
