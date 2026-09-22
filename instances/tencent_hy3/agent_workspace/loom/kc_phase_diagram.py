"""Practical phase diagram (random init) of reflexive Kuramoto K=K0*R^alpha.
P(lock) over seeds at uniform freq, N=150. Reveals THREE regimes:
 (E) emergence  : alpha<1  -> P=1 even at low K0 (continuous)
 (N) nucleation : alpha>1, K0 large -> P rises with K0 (finite seed)
 (F) frozen     : alpha>1, K0 small -> P~0 (stuck at random R)"""
import numpy as np, time
def kura(alpha,K0,N=150,T=40.0,dt=0.02,seed=0):
    rng=np.random.default_rng(seed)
    omega=rng.uniform(-1,1,N); theta=rng.uniform(0,2*np.pi,N)
    steps=int(T/dt)
    for _ in range(steps):
        z=np.mean(np.exp(1j*theta)); R=abs(z)
        K=K0*(R**alpha) if R>0 else 0.0
        theta+=dt*(omega+K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))
t0=time.time()
alphas=[1.0,1.2,1.4,1.6,1.8,2.0]; K0s=[5.0,10.0,20.0,40.0]; seeds=12
print("P(lock) rows=alpha, cols=K0")
for a in alphas:
    row=[]
    for K0 in K0s:
        lock=sum(1 for s in range(seeds) if kura(a,K0,seed=s)>0.8)
        row.append(f"{lock/seeds:.2f}")
    print(f" a={a}: "+" ".join(f"K{K0:.0f}={r}" for K0,r in zip(K0s,row)))
print("elapsed",round(time.time()-t0,1))
