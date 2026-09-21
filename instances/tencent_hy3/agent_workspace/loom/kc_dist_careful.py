"""Careful test: does the alpha<1 bootstrap depend on frequency distribution?
Compare UNIFORM vs TRUNCATED-CAUCHY (|u|<10) at small dt, long T, multiple seeds.
Also sweep K0 to see if larger K0 rescues Lorentzian locking. Track R(t)."""
import numpy as np, time

def kura(alpha, K0, dist, N=200, T=60.0, dt=0.01, seed=0):
    rng=np.random.default_rng(seed)
    if dist=='uniform':
        omega=rng.uniform(-1,1,N)
    else:  # truncated cauchy, |u|<10
        u=rng.standard_cauchy(N); u=np.clip(u,-10,10); omega=u
    theta=rng.uniform(0,2*np.pi,N)
    steps=int(T/dt); snap=[]
    for s in range(steps):
        z=np.mean(np.exp(1j*theta)); R=abs(z)
        K=K0*(R**alpha) if R>0 else 0.0
        theta+=dt*(omega+K*np.imag(np.exp(-1j*theta)*z))
        if s in (steps//4, steps//2, steps-1): snap.append(R)
    return snap

def run(dist,alpha,K0,seeds=3):
    rs=[kura(alpha,K0,dist,seed=s) for s in range(seeds)]
    # last-snapshot mean across seeds
    last=np.mean([r[-1] for r in rs]); mid=np.mean([r[1] for r in rs])
    return mid,last

t0=time.time()
for dist in ['uniform','tcauchy']:
    print(f"== {dist} == (report mid-T R, final R)")
    for K0 in [5.0,10.0,20.0]:
        line=[]
        for a in [0.5,0.7,0.9]:
            m,f=run(dist,a,K0)
            line.append(f"a{a},K0{K0:.0f}:mid={m:.2f},fin={f:.2f}")
        print("  "+" | ".join(line))
print("elapsed",round(time.time()-t0,1))
