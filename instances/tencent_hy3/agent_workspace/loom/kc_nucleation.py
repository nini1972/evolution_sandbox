"""Quantify: (1) alpha>1 NEVER locks even at huge K0 (universal failure),
(2) alpha<1 locks but the nucleation K0_ac depends on distribution breadth.
Compare uniform vs truncated-Cauchy frequencies. Measure max-R over K0 grid
(random init); report whether lock (R>0.6) is reachable and the min K0."""
import numpy as np, time

def kura(alpha, K0, dist, N=200, T=50.0, dt=0.01, seed=0):
    rng=np.random.default_rng(seed)
    if dist=='uniform': omega=rng.uniform(-1,1,N)
    else:
        u=rng.standard_cauchy(N); u=np.clip(u,-10,10); omega=u
    theta=rng.uniform(0,2*np.pi,N)
    steps=int(T/dt)
    for _ in range(steps):
        z=np.mean(np.exp(1j*theta)); R=abs(z)
        K=K0*(R**alpha) if R>0 else 0.0
        theta+=dt*(omega+K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

def reach(alpha,dist,seeds=2):
    Ks=np.array([3,5,8,12,20,40,80,160.0])
    best=0; kmin=None
    for K0 in Ks:
        rs=np.mean([kura(alpha,K0,dist,seed=s) for s in range(seeds)])
        if rs>0.6 and kmin is None: kmin=K0
        best=max(best,rs)
    return best,kmin

t0=time.time()
for dist in ['uniform','tcauchy']:
    print(f"== {dist} ==")
    for a in [0.3,0.5,0.7,0.9,1.1,1.5]:
        best,kmin=reach(a,dist)
        print(f"  alpha={a}: bestR={best:.2f}  K0_ac(min lock)={'None' if kmin is None else kmin}")
print("elapsed",round(time.time()-t0,1))
