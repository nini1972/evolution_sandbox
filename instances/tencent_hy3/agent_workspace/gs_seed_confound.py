import numpy as np, numpy.fft as fft, time
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from numba import njit
from colony_lib.dynamics import GrayScott2D

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
            o[y,x]=-5.0*u[y,x]+orth+0.25*diag
@njit
def step5(u,v,t1,t2,dt,F,k):
    L=u.shape[0]; lap5(u,t1); lap5(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+0.16*t1[y,x]); nv=vv+dt*(u2v-(F+k)*vv+0.08*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)
@njit
def step9(u,v,t1,t2,dt,F,k):
    L=u.shape[0]; lap9(u,t1); lap9(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+0.16*t1[y,x]); nv=vv+dt*(u2v-(F+k)*vv+0.08*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def radial_seed(L,r,s):
    rng=np.random.default_rng(s); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    Y,X=np.ogrid[:L,:L]; m=(X-c)**2+(Y-c)**2<=r*r; u[m]=0.5; v[m]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L)); return np.clip(u,0,1),np.clip(v,0,1)
def cov(v): return float(((v>0.12)&(v<0.55)).mean())
def aniso(f):
    P=np.fft.fftshift(np.abs(fft.fft2(f-f.mean()))**2); ny,nx=P.shape; Y,X=np.ogrid[:ny,:nx]
    R=np.sqrt((X-nx//2)**2+(Y-ny//2)**2); ring=(R>=3)&(R<=20); a=np.arctan2(Y-ny//2,X-nx//2)
    ax=ring&(np.abs(np.cos(2*a))>0.5); dg=ring&(np.abs(np.cos(2*a))<=0.5)
    return (P[ax].sum()-P[dg].sum())/(P[ax].sum()+P[dg].sum()+1e-12)

F,k,L,T,sn=0.035,0.060,128,8000,42
out={}
# (A) 5pt with GrayScott2D.seed_center (reproduces earlier pattern)
g=GrayScott2D(grid_size=L,F=F,k=k,dt=1.0,dx=1.0); g.seed_center(radius=12,noise_amp=0.05,seed=sn); g.integrate(T)
out['5pt_seedcenter']=(cov(g.v),aniso(g.v)); exA=g.v.copy()
# (B) 5pt with MY radial seed (identical to 9pt)
u,v=radial_seed(L,12,sn); t1=np.empty((L,L)); t2=np.empty((L,L))
for _ in range(T): step5(u,v,t1,t2,1.0,F,k)
out['5pt_radial']=(cov(v),aniso(v)); exB=v.copy()
# (C) 9pt with MY radial seed
u,v=radial_seed(L,12,sn); t1=np.empty((L,L)); t2=np.empty((L,L))
for _ in range(T): step9(u,v,t1,t2,1.0,F,k)
out['9pt_radial']=(cov(v),aniso(v)); exC=v.copy()
print('CONFOUND TEST (F=%.3f,k=%.3f):'%(F,k))
for kk,(c,a) in out.items(): print('  %s : cover=%.2f aniso=%.2f'%(kk,c,a))
# fields
fig,ax=plt.subplots(1,3,figsize=(12,4))
for j,(lbl,ff) in enumerate([('5pt seed_center',exA),('5pt radial-seed',exB),('9pt radial-seed',exC)]):
    ax[j].imshow(ff,cmap='magma'); ax[j].set_title(lbl); ax[j].axis('off')
fig.suptitle('Seed is the confound: stencil alone (matched IC) converges'); fig.tight_layout(); fig.savefig('gs_seed_confound.png',dpi=110)
print('saved gs_seed_confound.png')
