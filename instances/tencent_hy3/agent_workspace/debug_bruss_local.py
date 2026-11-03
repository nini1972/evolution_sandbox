import numpy as np, time
from numba import njit

# EXACT replication of brusselator_test4.py honest void+noise genesis
@njit(cache=True)
def lap(u):
    L=u.shape[0]
    out=np.empty_like(u)
    for y in range(L):
        for x in range(L):
            N=u[(y+1)%L,x]; S=u[(y-1)%L,x]; E=u[y,(x+1)%L]; W=u[y,(x-1)%L]
            NE=u[(y+1)%L,(x+1)%L]; NW=u[(y+1)%L,(x-1)%L]
            SE=u[(y-1)%L,(x+1)%L]; SW=u[(y-1)%L,(x-1)%L]
            out[y,x]=-u[y,x]+0.4*(N+S+E+W)+0.2*(NE+NW+SE+SW)
    return out

@njit(cache=True)
def step(u,v,a,b,Da,Db,L,dt):
    lu=lap(u); lv=lap(v)
    for y in range(L):
        for x in range(L):
            uv2=u[y,x]*u[y,x]*v[y,x]
            u[y,x]+=dt*(a-(b+1.0)*u[y,x]+uv2+Da*lu[y,x])
            v[y,x]+=dt*(b*u[y,x]-uv2+Db*lv[y,x])

L=120; a=0.8; b=1.6; Da=0.05; Db=1.0; dt=0.02; T=10000
np.random.seed(7)
u=np.full((L,L),a)+np.random.normal(0,1e-3,(L,L))
v=np.full((L,L),b/a)+np.random.normal(0,1e-3,(L,L))
print("INIT: u.std=%.5f v.std=%.5f"%(u.std(),v.std()))
for t in range(T):
    step(u,v,a,b,Da,Db,L,dt)
    if (t+1)%1000==0:
        fu=(u-u.mean())
        Fu=np.abs(np.fft.fft2(fu)); Fu[0,0]=0
        k=np.unravel_index(np.argmax(Fu),Fu.shape)
        dc=np.abs(np.fft.fft2(fu))[0,0]
        print("t=%5d u.std=%.4f v.std=%.4f peak/DC=%.1f FFTk=%s"%(t+1,u.std(),v.std(),Fu.max()/dc,(k[0],k[1])))
print("FINAL: u.std=%.4f v.std=%.4f  VOID-GENESIS=%s"%(u.std(),v.std(), bool(v.std()>0.05)))
np.save("debug_bruss_final_u.npy",u); np.save("debug_bruss_final_v.npy",v)
