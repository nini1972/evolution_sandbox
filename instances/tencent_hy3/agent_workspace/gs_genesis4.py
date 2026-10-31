import numpy as np, time, sys
from numba import njit
from scipy.ndimage import label
sys.path.insert(0,'.')
from gs_step import gs_step

@njit(cache=True)
def ic_near_trivial(L,seed,sd=0.01):
    np.random.seed(seed)
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=1.0 - np.random.random()*sd
        v[i//L,i%L]=0.0 + np.random.random()*sd
    return u,v

@njit(cache=True)
def ic_blanket(L,seed):
    np.random.seed(seed)
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=0.5; v[i//L,i%L]=0.25
    return u,v

def ndiv(v,th=0.1):
    s,nb=label((v>th).astype(np.int8)); return nb

Du,Dv,dt,L=0.16,0.08,1.0,100
Fs=np.round(np.arange(0.018,0.066,0.004),3)
print("=== genesis: near-trivial noise (u~1,v~0) Du=0.16 Dv=0.08 ===")
for F in Fs:
    k=0.060
    u,v=ic_near_trivial(L,13)
    for _ in range(40000): gs_step(u,v,F,k,Du,Dv,dt,L)
    print(f"  F={F:.3f} k={k:.3f}: N_div={ndiv(v):5d} vstd={np.nanstd(v):.3f} vmean={v.mean():.3f}")
