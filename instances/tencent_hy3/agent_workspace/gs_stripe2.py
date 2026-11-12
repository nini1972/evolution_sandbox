import numpy as np, numpy.fft as fft, time
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
def step(u,v,t1,t2,dt,F,k,Du,Dv,w,kind):
    L=u.shape[0]
    if kind==0: lap5(u,t1); lap5(v,t2)
    else: lap9(u,t1,w); lap9(v,t2,w)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x]); nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def ic_spots(L,sn,nsp=20,amp=0.5):
    rng=np.random.default_rng(sn); u=np.ones((L,L)); v=np.zeros((L,L))
    for _ in range(nsp):
        yy=rng.integers(4,L-4); xx=rng.integers(4,L-4); r=rng.integers(3,7)
        Y,X=np.ogrid[:L,:L]; m=(X-xx)**2+(Y-yy)**2<=r*r; u[m]=0.5; v[m]=amp
    u+=rng.uniform(-0.02,0.02,size=(L,L)); v+=rng.uniform(-0.02,0.02,size=(L,L)); return np.clip(u,0,1),np.clip(v,0,1)
def cov(v): return float(((v>0.12)&(v<0.55)).mean())
def A4(v):  # robust: angular 4-fold over fixed annulus 3<=R<=30
    P=np.fft.fftshift(np.abs(fft.fft2(v-v.mean()))**2)
    ny,nx=P.shape; Y,X=np.ogrid[:ny,:nx]; cx,cy=nx//2,ny//2
    kx=X-cx; ky=Y-cy; R=np.sqrt(kx*kx+ky*ky); ang=np.arctan2(ky,kx)
    m=(R>=3)&(R<=30); S=P[m].sum()
    if S<=1e-12: return 0.0
    return float((P[m]*np.cos(4*ang[m])).sum()/S)

cases=[(0.054,0.063),(0.046,0.063),(0.058,0.065)]  # coral, worms, maze
L,T,sn=160,30000,7
res={}; ex={}
t0=time.time()
for F,k in cases:
  u0,v0=ic_spots(L,sn)
  for lbl,kind,w in [('5pt',0,1.0),('9norm',1,2.0/3.0)]:
    u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
    for _ in range(T): step(u,v,t1,t2,1.0,F,k,0.16,0.08,w,kind)
    res[('%s_%.3f_%.3f'%(lbl,F,k))]=(cov(v),A4(v))
    if (F,k)==(0.054,0.063): ex[lbl]=v.copy()
    print('F=%.3f k=%.3f %s : cover=%.2f A4=%.3f'%(F,k,lbl,res[('%s_%.3f_%.3f'%(lbl,F,k))][0],res[('%s_%.3f_%.3f'%(lbl,F,k))][1]))
print('TOTAL %.1fs'%(time.time()-t0))
print('\nSYMMETRY-ONLY EFFECT (Delta A4 = 5pt - 9norm, Deff matched):')
for F,k in cases:
    d=res['5pt_%.3f_%.3f'%(F,k)][1]-res['9norm_%.3f_%.3f'%(F,k)][1]
    cv=res['5pt_%.3f_%.3f'%(F,k)][0]
    print('  F=%.3f k=%.3f  cover=%.2f  dA4=%.3f   (5pt=%.3f, 9norm=%.3f)'%(F,k,cv,d,res['5pt_%.3f_%.3f'%(F,k)][1],res['9norm_%.3f_%.3f'%(F,k)][1]))
import json; json.dump(dict(res=res,cases=cases),open('gs_stripe2.json','w'))
fig,ax=plt.subplots(1,2,figsize=(9,4)); ax[0].imshow(ex['5pt'],cmap='magma'); ax[0].set_title('5pt (coral F054,k063)'); ax[0].axis('off'); ax[1].imshow(ex['9norm'],cmap='magma'); ax[1].set_title('9norm iso (coral)'); ax[1].axis('off'); fig.tight_layout(); fig.savefig('gs_stripe2_fields.png',dpi=110)
xs=np.arange(len(cases)); wbar=0.35
fig,ax=plt.subplots(figsize=(9,4))
ax.bar(xs-wbar/2,[res['5pt_%.3f_%.3f'%(F,k)][1] for F,k in cases],wbar,label='5pt (anisotropic stencil)')
ax.bar(xs+wbar/2,[res['9norm_%.3f_%.3f'%(F,k)][1] for F,k in cases],wbar,label='9norm (isotropic, Deff=1)')
ax.set_xticks(xs); ax.set_xticklabels(['%s,%s'%(F,k) for F,k in cases]); ax.set_ylabel('A4 (4-fold anisotropy of stripes)'); ax.axhline(0,color='k',lw=0.5); ax.legend(); ax.set_title('Stripe orientation symmetry effect (matched IC & Deff)')
fig.tight_layout(); fig.savefig('gs_stripe2_A4.png',dpi=110)
print('saved gs_stripe2.json, gs_stripe2_fields.png, gs_stripe2_A4.png')
