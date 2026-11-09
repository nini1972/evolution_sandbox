#!/usr/bin/env python3
"""
DECISIVE BASIN-STRUCTURE TEST for the P4 tongue:  FINITE-K vs RIDDLED basins.

Take one locked attractor P0.  Add Gaussian noise of size delta to its phase-0
profile, re-converge, and measure whether the trajectory lands back on P0 or
JUMPS to a different P4 attractor (d_orbit > tol).  Sweep delta -> 0.

  Finite-K well-separated attractors : jump_fraction(delta) -> 0 as delta -> 0
                                       (only the measure-zero basin boundary jumps)
  Riddled / fractal basins          : jump_fraction(delta) -> c > 0 as delta -> 0
                                       (basin boundaries are dense in the basin)

Core cell: (r=3.87, eps=0.136), N=120.  Many trials per delta for binomial stats.
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N=120
def g(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    f=g(x,r); return (1.0-eps)*f+(0.5*eps)*(np.roll(f,1)+np.roll(f,-1))

def lock(r,eps,trans,x):
    x=x.copy()
    for _ in range(trans): x=coupled(x,r,eps)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps)
    return P

def d_orbit(P,Q):
    best=np.inf
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for s in range(N):
            d=float(np.max(np.abs(Pt-np.roll(Q,s,axis=0))))
            if d<best: best=d
    return best

r,eps=3.87,0.136
trans=12000
rng_master=np.random.default_rng(123)
x0=rng_master.random(N)
P0=lock(r,eps,trans,x0)
print(f"Locked P0.  Spread(amp)={P0.max()-P0.min():.4f}")

deltas=[1e-1,1e-2,3e-3,1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6,1e-7,1e-8]
nt=60
results=[]
for d in deltas:
    jumps=0; ds=[]
    for t in range(nt):
        ic=P0[:,0].copy() + d*(rng_master.standard_normal(N))
        ic=np.clip(ic,1e-12,1-1e-12)
        P=lock(r,eps,trans,ic)
        dist=d_orbit(P,P0)
        ds.append(dist); jumps += (dist>1e-3)
    frac=jumps/nt
    results.append((d,frac,jumps,nt,float(np.median([x for x in ds]))))
    print(f"  delta={d:8.1e}  jump_fraction={frac:6.3f}  ({jumps}/{nt})  median d_orbit={np.median(ds):.2e}")

fig,ax=plt.subplots(1,1,figsize=(7.5,5))
dd=[x[0] for x in results]; ff=[x[1] for x in results]
ax.semilogx(dd,ff,'o-',color='crimson',lw=1.5)
ax.axhline(0.5,color='gray',ls='--',lw=0.8)
ax.axhline(0.0,color='green',ls=':',lw=0.8)
ax.set_xlabel('perturbation size  delta  (Gaussian sigma)'); ax.set_ylabel('fraction JUMPING to a different P4 attractor')
ax.set_title(f'BASIN TEST  (r={r},eps={eps},N={N})\nfinite-K -> frac->0 ; riddled -> frac->c>0')
ax.set_ylim(-0.03,1.03); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('p4_basin_test.png',dpi=120); plt.close()
print("  saved p4_basin_test.png")

json.dump(dict(r=r,eps=eps,N=N,trans=trans,nt=nt,
               sweep=[[d,f,j,n,md] for d,f,j,n,md in results]),
          open('p4_basin_test.json','w'),indent=2)
print("saved p4_basin_test.json")
