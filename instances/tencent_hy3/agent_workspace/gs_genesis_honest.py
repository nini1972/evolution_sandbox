import numpy as np, time, sys
from numba import njit
from scipy.ndimage import label
sys.path.insert(0,'.')
from gs_step import gs_step

@njit(cache=True)
def ic_active_uniform(L,F,k,seed,noise):
    np.random.seed(seed)
    # uniform active homogeneous fixed point
    disc = np.sqrt(F*F + 4*(1-F)*(F+k)*(F+k))
    u0 = (-F + disc)/(2*(1-F))
    v0 = (F+k)/u0
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=u0 + (np.random.random()-0.5)*noise
        v[i//L,i%L]=v0 + (np.random.random()-0.5)*noise
    return u,v

def ndiv(v,th=0.1):
    s,nb=label((v>th).astype(np.int8)); return nb

Du,Dv,dt,L=0.16,0.08,1.0,100
print("=== HONEST genesis: uniform active state + infinitesimal noise (true symmetry breaking) ===")
print("u=1,v=0 void is a STABLE node -> blocked. Testing the OTHER homogeneous fixed point.")
for F,k in [(0.030,0.062),(0.034,0.061),(0.038,0.060),(0.042,0.061),(0.050,0.063),(0.054,0.063),(0.062,0.061),(0.070,0.061)]:
    disc = np.sqrt(F*F + 4*(1-F)*(F+k)*(F+k))
    u0 = (-F + disc)/(2*(1-F)); v0=(F+k)/u0
    u,v=ic_active_uniform(L,F,k,5,0.01)
    for _ in range(25000): gs_step(u,v,F,k,Du,Dv,dt,L)
    print(f"  F={F:.3f} k={k:.3f} (u0={u0:.3f},v0={v0:.3f}): N_div={ndiv(v):5d} vstd={np.nanstd(v):.3f} vmean={v.mean():.3f}")
