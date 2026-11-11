import numpy as np, numpy.fft as fft, time, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from numba import njit

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def lap9(u,o,w):  # w=1 raw ; w=2/3 -> Deff matched to 5pt
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
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x])
            nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu)
            v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def seed(L,r,s):
    rng=np.random.default_rng(s); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    Y,X=np.ogrid[:L,:L]; mask=(X-c)**2+(Y-c)**2<=r*r
    u[mask]=0.5; v[mask]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
    return np.clip(u,0,1),np.clip(v,0,1)

def cov(v): return float(((v>0.12)&(v<0.55)).mean())
def aniso(field):
    P=np.fft.fftshift(np.abs(fft.fft2(field-field.mean()))**2)
    ny,nx=P.shape; Y,X=np.ogrid[:ny,:nx]; R=np.sqrt((X-nx//2)**2+(Y-ny//2)**2)
    ring=(R>=3)&(R<=20); ang=np.arctan2(Y-ny//2,X-nx//2)
    ax=ring&(np.abs(np.cos(2*ang))>0.5); dg=ring&(np.abs(np.cos(2*ang))<=0.5)
    return (P[ax].sum()-P[dg].sum())/(P[ax].sum()+P[dg].sum()+1e-12)

F_list=[0.030,0.035,0.046]; k_list=[0.050,0.056,0.060]; L=128; T=8000; sn=42
res={}; ex={}
t0=time.time()
for F in F_list:
  for k in k_list:
    for kind,w,lbl in [(0,1.0,'5pt'),(1,1.0,'9raw'),(1,2.0/3.0,'9norm')]:
        u,v=seed(L,12,sn)
        t1=np.empty((L,L)); t2=np.empty((L,L))
        for _ in range(T): step(u,v,t1,t2,1.0,F,k,0.16,0.08,w,kind)
        res[('%s_%.3f_%.3f'%(lbl,F,k))]=(cov(v),aniso(v))
        if (F,k)==(0.035,0.060): ex[lbl]=v.copy()
        print('F=%.3f k=%.3f %s c=%.2f a=%.2f'%(F,k,lbl,res[('%s_%.3f_%.3f'%(lbl,F,k))][0],res[('%s_%.3f_%.3f'%(lbl,F,k))][1]))
print('TOTAL %.1fs'%(time.time()-t0))
json.dump(dict(res=res,F_list=F_list,k_list=k_list),open('gs_control3.json','w'))
# summary bars
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
xs=np.arange(len(k_list)); wbar=0.27
for i,F in enumerate(F_list):
  c5=[res['5pt_%.3f_%.3f'%(F,k)][0] for k in k_list]
  c9r=[res['9raw_%.3f_%.3f'%(F,k)][0] for k in k_list]
  c9n=[res['9norm_%.3f_%.3f'%(F,k)][0] for k in k_list]
  ax[0].bar(xs+(i-1)*wbar,c5,wbar,label='5pt F=%.3f'%F)
  ax[0].bar(xs+(i-1)*wbar+wbar,c9r,wbar,alpha=0.5)
  ax[0].bar(xs+(i-1)*wbar+2*wbar,c9n,wbar,alpha=0.3)
ax[0].set_xticks(xs); ax[0].set_xticklabels(['%.3f'%k for k in k_list]); ax[0].set_title('cover (sole var = stencil)'); ax[0].set_xlabel('k')
fig.tight_layout(); fig.savefig('gs_control3.png',dpi=110)
# example fields at (0.035,0.060)
fig,ax=plt.subplots(1,3,figsize=(12,4))
for j,lbl in enumerate(['5pt','9raw','9norm']):
    ax[j].imshow(ex[lbl],cmap='magma'); ax[j].set_title(lbl+' (F0.035,k0.060)'); ax[j].axis('off')
fig.tight_layout(); fig.savefig('gs_control3_fields.png',dpi=110)
print('saved gs_control3.json, gs_control3.png, gs_control3_fields.png')
