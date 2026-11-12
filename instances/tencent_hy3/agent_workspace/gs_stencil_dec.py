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
def cov(v): return float(((v>0.12)&(v<0.55)).mean())
def aniso(f):
    P=np.fft.fftshift(np.abs(fft.fft2(f-f.mean()))**2); ny,nx=P.shape; Y,X=np.ogrid[:ny,:nx]
    R=np.sqrt((X-nx//2)**2+(Y-ny//2)**2); ring=(R>=3)&(R<=20); a=np.arctan2(Y-ny//2,X-nx//2)
    ax=ring&(np.abs(np.cos(2*a))>0.5); dg=ring&(np.abs(np.cos(2*a))<=0.5)
    return (P[ax].sum()-P[dg].sum())/(P[ax].sum()+P[dg].sum()+1e-12)

F,k,L,T,sn=0.035,0.060,128,8000,42
out={}; ex={}
# Build SAME seed_center IC, feed to both steppers
g=GrayScott2D(grid_size=L,F=F,k=k,dt=1.0,dx=1.0); g.seed_center(radius=12,noise_amp=0.05,seed=sn)
u0=g.u.copy(); v0=g.v.copy()
# report IC structure
Y,X=np.ogrid[:L,:L]; c=L//2; r=12; inside=((X-c)**2+(Y-c)**2)<=r*r
print('seed_center IC: nonzero-v pixels=%d (vs my radial %d)'%(int((v0>0).sum()), int(inside.sum())))
# 5pt on seed_center
u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
for _ in range(T): step5(u,v,t1,t2,1.0,F,k)
out['5pt_seedcenter']=(cov(v),aniso(v)); ex['5pt']=v.copy()
# 9pt on SAME seed_center
u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
for _ in range(T): step9(u,v,t1,t2,1.0,F,k)
out['9pt_seedcenter']=(cov(v),aniso(v)); ex['9pt']=v.copy()
print('DECISIVE (same seed_center IC, vary stencil):')
for kk,(c,a) in out.items(): print('  %s : cover=%.2f aniso=%.2f'%(kk,c,a))
fig,ax=plt.subplots(1,2,figsize=(9,4))
ax[0].imshow(ex['5pt'],cmap='magma'); ax[0].set_title('5pt + seed_center'); ax[0].axis('off')
ax[1].imshow(ex['9pt'],cmap='magma'); ax[1].set_title('9pt + seed_center'); ax[1].axis('off')
fig.suptitle('Same IC, stencil-only variable (F=%.3f,k=%.3f)'%(F,k)); fig.tight_layout(); fig.savefig('gs_stencil_dec.png',dpi=110)
print('saved gs_stencil_dec.png')
