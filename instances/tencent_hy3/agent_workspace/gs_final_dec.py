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
def step(u,v,t1,t2,dt,F,k,Du,Dv,w,kind):
    L=u.shape[0]
    if kind==0: lap5(u,t1); lap5(v,t2)
    else: lap9(u,t1,w); lap9(v,t2,w)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x]); nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)
def seed(L,r,s):
    rng=np.random.default_rng(s); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    Y,X=np.ogrid[:L,:L]; m=(X-c)**2+(Y-c)**2<=r*r; u[m]=0.5; v[m]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L)); return np.clip(u,0,1),np.clip(v,0,1)
def cov(v): return float(((v>0.12)&(v<0.55)).mean())
def aniso(f):
    P=np.fft.fftshift(np.abs(fft.fft2(f-f.mean()))**2); ny,nx=P.shape; Y,X=np.ogrid[:ny,:nx]
    R=np.sqrt((X-nx//2)**2+(Y-ny//2)**2); ring=(R>=3)&(R<=20); a=np.arctan2(Y-ny//2,X-nx//2)
    ax=ring&(np.abs(np.cos(2*a))>0.5); dg=ring&(np.abs(np.cos(2*a))<=0.5)
    return (P[ax].sum()-P[dg].sum())/(P[ax].sum()+P[dg].sum()+1e-12)

F,k,L,T,r,sn=0.035,0.060,96,7000,8,42
u0,v0=seed(L,r,sn)
print('small radial seed (r=%d): v-nonzero=%d'%(r,int((v0>0).sum())))
res={}; ex={}
for lbl,kind,w in [('5pt',0,1.0),('9raw',1,1.0),('9norm',1,2.0/3.0)]:
    u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
    for _ in range(T): step(u,v,t1,t2,1.0,F,k,0.16,0.08,w,kind)
    res[lbl]=(cov(v),aniso(v)); ex[lbl]=v.copy()
    print('  %s : cover=%.2f aniso=%.2f'%(lbl,res[lbl][0],res[lbl][1]))
# Interpretation
c5,a5=res['5pt']; cr,ar=res['9raw']; cn,an_=res['9norm']
print('\nINTERPRETATION:')
if c5!=cr:
    if cn==cr: print('  SYMMETRY (anisotropy) selects form: 5pt(aniso) != 9norm(iso,Deff matched)')
    elif cn==c5: print('  DIFFUSION MAGNITUDE (Deff) selects form: 5pt & 9norm (Deff=1) == ; 9raw(Deff1.5) !=')
    else: print('  MIXED / scale-dependent')
else:
    print('  STENCIL IRRELEVANT at this scale: 5pt == 9raw == 9norm (outcome set by IC only)')
fig,ax=plt.subplots(1,3,figsize=(12,4))
for j,lbl in enumerate(['5pt','9raw','9norm']):
    ax[j].imshow(ex[lbl],cmap='magma'); ax[j].set_title('%s c=%.2f'%(lbl,res[lbl][0])); ax[j].axis('off')
fig.suptitle('Same SMALL seed, vary stencil only (F=%.3f,k=%.3f,r=%d)'%(F,k,r)); fig.tight_layout(); fig.savefig('gs_final_dec.png',dpi=110)
print('saved gs_final_dec.png')
