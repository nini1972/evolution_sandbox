import numpy as np, time, sys
from numba import njit
from scipy.ndimage import label
sys.path.insert(0,'.')
from gs_step import gs_step

@njit(cache=True)
def seed_patches(L,seed,nseed=40,ps=4):
    np.random.seed(seed)
    u=np.ones((L,L)); v=np.zeros((L,L))
    for _ in range(nseed):
        x=int(np.random.random()*(L-ps)); y=int(np.random.random()*(L-ps))
        for i in range(ps):
            for j in range(ps):
                u[x+i,y+j]=0.5; v[x+i,y+j]=0.25
    return u,v

def ndiv(v,th=0.1):
    s,nb=label((v>th).astype(np.int8)); return nb

Du,Dv,dt,L=0.16,0.08,1.0,100
print("=== seeded-patch genesis (nseed=40) ===")
for F,k in [(0.030,0.062),(0.034,0.061),(0.042,0.061),(0.054,0.063),(0.062,0.061)]:
    u,v=seed_patches(L,3)
    for _ in range(20000): gs_step(u,v,F,k,Du,Dv,dt,L)
    print(f"  F={F:.3f} k={k:.3f}: N_div={ndiv(v):5d} vstd={np.nanstd(v):.3f} vmean={v.mean():.3f}")
