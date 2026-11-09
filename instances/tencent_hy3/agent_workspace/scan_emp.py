import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, time, json

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*u[y,x]+1.0*orth+0.25*diag

@njit
def step(u,v,t1,t2,applyf,dt,F,k,Du,Dv):
    L=u.shape[0]
    applyf(u,t1); applyf(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x])
            nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            if nu<0: nu=0.0
            elif nu>1: nu=1.0
            if nv<0: nv=0.0
            elif nv>1: nv=1.0
            u[y,x]=nu; v[y,x]=nv

def run(applyf,F,k,Du,Dv,seed,L=128,dt=1.0,T=6000):
    rng=np.random.default_rng(seed)
    # full-field noise seed (classic robust nucleation)
    u=1.0-0.5*rng.random((L,L))
    v=0.25*rng.random((L,L))
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for t in range(T):
        step(u,v,t1,t2,applyf,dt,F,k,Du,Dv)
        if not np.isfinite(u).all():
            return u,v,'NaN@%d'%t
    return u,v,'ok'

Du,Dv=0.16,0.08
params=[(0.030,0.056),(0.036,0.060),(0.046,0.063),(0.054,0.063),
        (0.062,0.061),(0.070,0.061),(0.078,0.061),(0.090,0.057)]
results=[]
for (F,k) in params:
    u,v,st=run(lap5,F,k,Du,Dv,11)
    cover=(v>0.2).mean()
    um=u.mean(); vm=v.mean()
    print("F=%.3f k=%.3f  status=%s  u_mean=%.3f v_mean=%.4f cover(v>0.2)=%.3f"%(F,k,st,um,vm,cover))
    results.append(dict(F=F,k=k,status=st,u_mean=um,v_mean=vm,cover=float(cover)))
    if st=='ok' and 0.1<cover<0.95:
        plt.imsave("emp_F%.3f_k%.3f.png"%(F,k),u,cmap='magma')

json.dump(results,open('scan_emp.json','w'),indent=2,default=str)
print("DONE")
