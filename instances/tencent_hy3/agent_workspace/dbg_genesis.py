import numpy as np, sys
sys.path.insert(0,'.')
from gs_step import gs_step
from numba import njit
@njit(cache=True)
def random_ic(L,seed):
    np.random.seed(seed)
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=0.9 + np.random.random()*0.1   # [0.9,1.0]
        v[i//L,i%L]=0.0 + np.random.random()*0.1   # [0.0,0.1]
    return u,v
L=40
u,v=random_ic(L,42)
print("ic u range",np.nanmin(u),np.nanmax(u),"v",np.nanmin(v),np.nanmax(v))
F,k,Du,Dv,dt=0.030,0.057,0.037,0.06,1.0
for t in range(50):
    gs_step(u,v,F,k,Du,Dv,dt,L)
    if t%10==0:
        print(t,"u",np.nanmin(u),np.nanmax(u),"v",np.nanmin(v),np.nanmax(v))
