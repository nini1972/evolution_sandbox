import numpy as np, time, sys
from numba import njit
from scipy.ndimage import label
sys.path.insert(0,'.')
from gs_step import gs_step

@njit(cache=True)
def random_ic(L,seed,uv0=0.5,vv0=0.25,amp=0.5):
    np.random.seed(seed)
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=uv0 + (np.random.standard_normal())*amp
        v[i//L,i%L]=vv0 + (np.random.standard_normal())*amp
    return u,v

def ndiv(v,th=0.1):
    m=(v>th).astype(np.int8)
    s,nb=label(m); return nb

Du,Dv,dt,L,T=0.037,0.06,1.0,90,20000
print("=== GS spontaneous genesis from RANDOM IC (no seed region) ===")
cands=[(0.018,0.050),(0.022,0.051),(0.026,0.053),(0.030,0.057),(0.034,0.061),(0.036,0.060),(0.042,0.059),(0.054,0.063)]
for F,k in cands:
    u,v=random_ic(L,42)
    t0=time.time()
    for _ in range(T): gs_step(u,v,F,k,Du,Dv,dt,L)
    d=time.time()-t0
    nd=ndiv(v)
    print(f"  F={F:.3f} k={k:.3f}: N_div={nd:4d}  vstd={v.std():.3f}  ({d:.1f}s)")
