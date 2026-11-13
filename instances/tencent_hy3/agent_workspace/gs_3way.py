import numpy as np
from numba import njit
try:
    from colony_lib.dynamics import GrayScott2D
    HAVE=True
except Exception as e:
    HAVE=False; print('no lib',e)

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]
@njit
def mystep(u,v,t1,t2,dt,F,k,Du,Dv):
    L=u.shape[0]; lap5(u,t1); lap5(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; uv2=uu*vv*vv
            nu=uu+dt*(F*(1.0-uu)-uv2+Du*t1[y,x]); nv=vv+dt*(uv2-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

F,k,L,dt=0.035,0.060,128,1.0
horizons=[100,500,2000,5000,10000]
def cov(v): return float((v>0.2).mean())
def seed(L,r,sn=42):
    rng=np.random.default_rng(sn); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    u[c-r:c+r,c-r:c+r]=0.5; v[c-r:c+r,c-r:c+r]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
    return np.clip(u,0,1),np.clip(v,0,1)

u0,v0=seed(L,10)
print('3-way cover(v>0.2) at horizons:')
print('  %8s | %8s | %8s | %8s'%('steps','MY','lib.step','lib.JIT'))
for T in horizons:
    # MY
    u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
    for _ in range(T): mystep(u,v,t1,t2,dt,F,k,0.16,0.08)
    mycov=cov(v)
    # lib.step loop (non-JIT)
    if HAVE:
        sim=GrayScott2D(grid_size=L,F=F,k=k,dt=dt); sim.seed_center(radius=10,seed=42)
        for _ in range(T): sim.step()
        stepcov=cov(sim.v)
        # lib.JIT integrate
        sim2=GrayScott2D(grid_size=L,F=F,k=k,dt=dt); sim2.seed_center(radius=10,seed=42); sim2.integrate(steps=T)
        jitcov=cov(sim2.v)
        print('  %8d | %8.3f | %8.3f | %8.3f'%(T,mycov,stepcov,jitcov))
    else:
        print('  %8d | %8.3f |   n/a    |   n/a'%(T,mycov))
