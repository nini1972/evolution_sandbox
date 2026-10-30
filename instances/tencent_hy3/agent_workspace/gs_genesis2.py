import numpy as np, time, sys
from numba import njit
from scipy.ndimage import label
sys.path.insert(0,'.')
from gs_step import gs_step

@njit(cache=True)
def random_ic(L,seed):
    np.random.seed(seed)
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=0.5 + np.random.random()*0.5   # [0.5,1.0]
        v[i//L,i%L]=0.0 + np.random.random()*0.3   # [0.0,0.3]
    return u,v

def ndiv(v,th=0.1):
    s,nb=label((v>th).astype(np.int8)); return nb

Du,Dv,dt,L=0.037,0.06,1.0,90
print("=== GS genesis from finite-amplitude noise ===")
cands=[(0.030,0.062),(0.034,0.061),(0.036,0.060),(0.038,0.061),(0.040,0.062),(0.046,0.063),(0.054,0.063),(0.062,0.061)]
for F,k in cands:
    u,v=random_ic(L,7)
    t0=time.time()
    for _ in range(30000): gs_step(u,v,F,k,Du,Dv,dt,L)
    d=time.time()-t0
    print(f"  F={F:.3f} k={k:.3f}: N_div={ndiv(v):4d}  vstd={np.nanstd(v):.3f}  ({d:.1f}s)")
