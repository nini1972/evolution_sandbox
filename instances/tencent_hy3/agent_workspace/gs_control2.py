import numpy as np, numpy.fft as fft, time, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from numba import njit
from colony_lib.dynamics import GrayScott2D

@njit
def lap9_norm(u,o,w):
    # isotropic 9pt kernel scaled by w (w=2/3 -> small-k symbol = -|k|^2, same as 5pt; zero-sum preserved)
    # center weight = -5*w ; orth weight = w ; diag weight = 0.25*w
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*w*u[y,x]+w*orth+0.25*w*diag

@njit
def step9(u,v,t1,t2,dt,F,k,Du,Dv,w):
    L=u.shape[0]; lap9_norm(u,t1,w); lap9_norm(v,t2,w)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x])
            nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu)
            v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def cov(v): return float(((v>0.12)&(v<0.55)).mean())
def aniso(field):
    P=np.fft.fftshift(np.abs(fft.fft2(field-field.mean()))**2)
    ny,nx=P.shape; Y,X=np.ogrid[:ny,:nx]; R=np.sqrt((X-nx//2)**2+(Y-ny//2)**2)
    ring=(R>=3)&(R<=20); ang=np.arctan2(Y-ny//2,X-nx//2)
    ax=ring&(np.abs(np.cos(2*ang))>0.5); dg=ring&(np.abs(np.cos(2*ang))<=0.5)
    return (P[ax].sum()-P[dg].sum())/(P[ax].sum()+P[dg].sum()+1e-12)

F_list=[0.030,0.035,0.046,0.060]; k_list=[0.040,0.050,0.056,0.060,0.066]; L=96; T=7000; seed=42
C5={};A5={};C9={};A9={};C9n={};A9n={}
t0=time.time()
for F in F_list:
  for k in k_list:
    g5=GrayScott2D(grid_size=L,F=F,k=k,dt=1.0,dx=1.0); g5.seed_center(radius=8,noise_amp=0.05,seed=seed); g5.integrate(T)
    rng=np.random.default_rng(seed); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2; r=8
    u[c-r:c+r,c-r:c+r]=0.5; v[c-r:c+r,c-r:c+r]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L)); u=np.clip(u,0,1); v=np.clip(v,0,1)
    t1=np.empty((L,L)); t2=np.empty((L,L)); uu=u.copy(); vv=v.copy(); un=u.copy(); vnn=v.copy()
    for _ in range(T): step9(uu,vv,t1,t2,1.0,F,k,0.16,0.08,1.0)      # raw 9pt (Deff 1.5x)
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for _ in range(T): step9(un,vnn,t1,t2,1.0,F,k,0.16,0.08,2.0/3.0) # normalized 9pt (Deff=1, isotropy only)
    C5[(F,k)]=cov(g5.v); A5[(F,k)]=aniso(g5.v); C9[(F,k)]=cov(vv); A9[(F,k)]=aniso(vv); C9n[(F,k)]=cov(vnn); A9n[(F,k)]=aniso(vnn)
    print('F=%.3f k=%.3f | 5pt c=%.2f a=%.2f | 9raw c=%.2f a=%.2f | 9norm c=%.2f a=%.2f'%(F,k,C5[(F,k)],A5[(F,k)],C9[(F,k)],A9[(F,k)],C9n[(F,k)],A9n[(F,k)]))
print('TOTAL %.1fs'%(time.time()-t0))
def sk(d): return {('%s_%s'%(F,k)):(d[(F,k)]) for F in F_list for k in k_list}
json.dump(dict(F_list=F_list,k_list=k_list,C5=sk(C5),A5=sk(A5),C9=sk(C9),A9=sk(A9),C9n=sk(C9n),A9n=sk(A9n)),open('gs_control2.json','w'))
# plot
fig,ax=plt.subplots(1,2,figsize=(13,4.5))
xs=np.arange(len(k_list)); w=0.27
for i,F in enumerate(F_list):
  c5=[C5[(F,k)] for k in k_list]; c9n=[C9n[(F,k)] for k in k_list]
  a5=[A5[(F,k)] for k in k_list]; a9n=[A9n[(F,k)] for k in k_list]
  ax[0].bar(xs+(i-1)*w,c5,w,label='5pt F=%.3f'%F,color='C%d'%i)
  ax[0].bar(xs+(i-1)*w,w,c9n,w,alpha=0.5,color='C%d'%i)
  ax[1].bar(xs+(i-1)*w,a5,w,label='5pt F=%.3f'%F,color='C%d'%i)
  ax[1].bar(xs+(i-1)*w,w,a9n,w,alpha=0.5,color='C%d'%i)
ax[0].set_xticks(xs); ax[0].set_xticklabels(['%.3f'%k for k in k_list]); ax[0].set_xlabel('k'); ax[0].set_ylabel('cover'); ax[0].set_title('cover: 5pt(solid) vs 9norm(Deff=1, faint)')
ax[1].set_xticks(xs); ax[1].set_xticklabels(['%.3f'%k for k in k_list]); ax[1].set_xlabel('k'); ax[1].set_ylabel('E4 aniso'); ax[1].set_title('aniso: 5pt(solid) vs 9norm(Deff=1, faint)')
ax[0].legend(fontsize=8); fig.tight_layout(); fig.savefig('gs_control2.png',dpi=110)
print('saved gs_control2.json, gs_control2.png')
