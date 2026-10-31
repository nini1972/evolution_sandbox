import numpy as np, sys
from numba import njit
from scipy.ndimage import label
sys.path.insert(0,'.')
from gs_step import gs_step

@njit(cache=True)
def seed_disk(L,R,u0=1.0,v0=0.0,uu=0.5,vv=0.25,seed=1):
    np.random.seed(seed)
    u=np.ones((L,L)); v=np.zeros((L,L))
    c=L//2
    for i in range(L):
        for j in range(L):
            if (i-c)**2+(j-c)**2 <= R*R:
                u[i,j]=uu; v[i,j]=vv
    return u,v

def ndiv(v,th=0.1):
    s,nb=label((v>th).astype(np.int8)); return nb

def survives(F,k,R,L=120,steps=20000,th=0.1):
    u,v=seed_disk(L,R)
    for _ in range(steps):
        gs_step(u,v,F,k,0.16,0.08,1.0,L)
    # survive if pattern persists and has spread beyond initial disk (periphery active)
    return ndiv(v)>5 and v.max()>th

print("=== Nucleation barrier: minimal seed radius R* that triggers sustained genesis ===")
results={}
for F,k in [(0.030,0.062),(0.034,0.061),(0.038,0.060),(0.042,0.061),(0.054,0.063),(0.062,0.061)]:
    lo,hi=1,40
    Rstar=None
    # coarse scan then refine
    Rs=[2,3,4,5,6,8,10,12,15,20,25,30]
    last=False
    for R in Rs:
        s=survives(F,k,R)
        if s and not last:
            Rstar=R; break
        last=s
    results[(F,k)]=Rstar
    print(f"  F={F:.3f} k={k:.3f}: R* ~ {Rstar} (disk survives if R>=R*)")
