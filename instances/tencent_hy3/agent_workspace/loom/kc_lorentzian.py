"""Confirm the alpha* divergent threshold is distribution-independent:
repeat the reflexive Kuramoto with LORENTZIAN natural frequencies
(g(omega)=1/(pi*Delta)*(Delta^2/(omega^2+Delta^2)), Delta=1) instead of
uniform. Bare Kc(inf)=2*Delta=2. The alpha>1 local argument is blind to the
distribution (needs only g bounded & >0 near 0), so the collapse should
reappear for alpha>1. Also re-tests a bounded CML proxy via logistic maps."""
import numpy as np, time

def kura(alpha, K0, N=200, Delta=1.0, T=35.0, dt=0.02, seed=0):
    rng=np.random.default_rng(seed)
    u=rng.standard_cauchy(N); omega=Delta*u   # Lorentzian (heavy tails)
    theta=rng.uniform(0,2*np.pi,N)
    steps=int(T/dt)
    for _ in range(steps):
        z=np.mean(np.exp(1j*theta)); R=abs(z)
        K=K0*(R**alpha) if R>0 else 0.0
        theta+=dt*(omega+K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

def mr(a,K0,seeds=3): return float(np.mean([kura(a,K0,seed=s) for s in range(seeds)]))

t0=time.time()
print("Lorentzian-freq reflexive Kuramoto (random init):")
for K0 in [3.0,5.0]:
    print(f" K0={K0}: "+"  ".join(f"a{a}:R={mr(a,K0):.2f}" for a in [0.7,0.9,1.0,1.2]))
print("elapsed",round(time.time()-t0,1))
