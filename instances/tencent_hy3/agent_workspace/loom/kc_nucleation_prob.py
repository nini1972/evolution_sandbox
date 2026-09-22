"""Nucleation-probability study (small/fast). For reflexive Kuramoto with
uniform freq, measure P(lock) over random seeds as function of alpha and K0.
Confirms: alpha<1 -> P(lock)~1 (continuous emergence); alpha>1 -> P(lock)
rises with K0 (nucleation), never from infinitesimal disorder."""
import numpy as np, time
def kura(alpha,K0,N=120,T=30.0,dt=0.02,seed=0):
    rng=np.random.default_rng(seed)
    omega=rng.uniform(-1,1,N); theta=rng.uniform(0,2*np.pi,N)
    steps=int(T/dt)
    for _ in range(steps):
        z=np.mean(np.exp(1j*theta)); R=abs(z)
        K=K0*(R**alpha) if R>0 else 0.0
        theta+=dt*(omega+K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))
t0=time.time()
for a in [0.9,1.0,1.1,1.3]:
    line=[]
    for K0 in [5.0,10.0,20.0,40.0]:
        seeds=10; lock=sum(1 for s in range(seeds) if kura(a,K0,seed=s)>0.8)
        line.append(f"K0{K0:.0f}:P={lock/seeds:.2f}")
    print(f"alpha={a}: "+" ".join(line))
print("elapsed",round(time.time()-t0,1))
