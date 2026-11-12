import numpy as np, numpy.fft as fft
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from numba import njit

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]
@njit
def lap9(u,o,w):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*w*u[y,x]+w*orth+0.25*w*diag
@njit
def step5(u,v,t1,t2,dt,F,k,Du,Dv):
    L=u.shape[0]; lap5(u,t1); lap5(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x]); nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def diag(L,F,k,sn,T,dx=1.0,Du=0.16,Dv=0.08):
    rng=np.random.default_rng(sn); u=np.ones((L,L)); v=np.zeros((L,L))
    c=L//2; r=10; Y,X=np.ogrid[:L,:L]; m=(X-c)**2+(Y-c)**2<=r*r
    u[m]=0.5; v[m]=0.25; u+=rng.uniform(-0.01,0.01,size=(L,L)); v+=rng.uniform(-0.01,0.01,size=(L,L))
    u=np.clip(u,0,1); v=np.clip(v,0,1)
    t1=np.empty((L,L)); t2=np.empty((L,L)); dt=dx*dx*0.9
    for _ in range(T): step5(u,v,t1,t2,dt,F,k,Du,Dv)
    fv=v.copy()
    return fv

# Known-good Pearson regimes
tests=[(0.035,0.065,'negatons/holes'),(0.062,0.061,'mitosis'),(0.018,0.051,'chaos'),(0.054,0.063,'coral')]
L,T,sn=128,15000,42
print('INTEGRATOR DIAGNOSTIC (5pt, dx=1, dt=0.9*dx^2):')
for F,k,name in tests:
    v=diag(L,F,k,sn,T)
    frac_band=float(((v>0.12)&(v<0.55)).mean())
    print('  F=%.3f k=%.3f %-16s v[min=%.3f mean=%.3f max=%.3f] std=%.3f band=%.2f'%(F,k,name,v.min(),v.mean(),v.max(),v.std(),frac_band))
    plt.figure(figsize=(4,4)); plt.imshow(v,cmap='magma'); plt.title('F%.3f k%.3f %s'%(F,k,name)); plt.axis('off'); plt.tight_layout(); plt.savefig('diag_%.3f_%.3f.png'%(F,k),dpi=90); plt.close()
print('saved diagnostic pngs')
