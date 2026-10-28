import numpy as np
from numba import njit

@njit(cache=True)
def schnak(a,b,Du,Dv,dt,L,T,seed,sigma0,noise_each):
    u=np.ones((L,L))*(a+b)
    v=np.ones((L,L))*(b/((a+b)**2))
    np.random.seed(seed)
    u+=np.random.standard_normal((L,L))*sigma0
    v+=np.random.standard_normal((L,L))*sigma0
    for t in range(T):
        lapu=np.empty_like(u); lapv=np.empty_like(v)
        for x in range(L):
            for y in range(L):
                lapu[x,y]=u[(x+1)%L,y]+u[(x-1)%L,y]+u[x,(y+1)%L]+u[x,(y-1)%L]-4*u[x,y]
                lapv[x,y]=v[(x+1)%L,y]+v[(x-1)%L,y]+v[x,(y+1)%L]+v[x,(y-1)%L]-4*v[x,y]
        for i in range(L*L):
            x=i//L; y=i%L
            uv=u[x,y]*u[x,y]*v[x,y]
            u[x,y]+=(Du*lapu[x,y]+a-u[x,y]+uv)*dt
            v[x,y]+=(Dv*lapv[x,y]+b-uv)*dt
        if noise_each>0:
            u+=np.random.standard_normal((L,L))*noise_each
            v+=np.random.standard_normal((L,L))*noise_each
    return v

a,b,Du,Dv,dt,L=(0.1,0.9,0.01,0.1,0.2,100)
print("=== single-seed genesis vs seed amplitude (no continuous noise), T=25000 ===")
for sigma0 in [1e-3,3e-3,1e-2,5e-2]:
    v=schnak(a,b,Du,Dv,dt,L,25000,42,sigma0,0.0)
    print(f"  seed amp={sigma0:.4f}: v std = {v.std():.5f}  -> {'FORM' if v.std()>0.01 else 'void'}")
print("=== continuous tiny noise amplitude sweep ===")
for na in [1e-5,3e-5,1e-4,3e-4,1e-3]:
    v=schnak(a,b,Du,Dv,dt,L,25000,42,1e-4,na)
    print(f"  noise amp={na:.5f}: v std = {v.std():.5f}")
