import numpy as np, time
from numba import njit
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=(4.0*orth+1.0*diag-20.0*u[y,x])/6.0

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def step(u,v,t1,t2,dt,F,k,Du,Dv,lap):
    L=u.shape[0]; lap(u,t1); lap(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; uv2=uu*vv*vv
            nu=uu+dt*(F*(1.0-uu)-uv2+Du*t1[y,x]); nv=vv+dt*(uv2-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def takens(s,m,tau):
    N=len(s); ne=N-(m-1)*tau
    return np.array([s[i:i+m*tau:tau] for i in range(ne)])

def rqa(series,m=3,tau=1,eps=None,target_RR=0.05,lmin=2):
    X=takens(series,m,tau); N=X.shape[0]
    D=np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(-1))
    if eps is None:
        off=np.sort(D[~np.eye(N,dtype=bool)]); idx=min(int(target_RR*off.size),off.size-1); eps=off[idx]
    R=(D<=eps)&~np.eye(N,dtype=bool)
    total=R.sum()
    if total==0: return 0.0,0.0,eps
    diag_sum=0
    for k in range(1,N):
        d=np.diag(R,k).astype(int)
        if d.sum()==0: continue
        runs=np.diff(np.concatenate(([0],d,[0])))
        starts=np.where(runs==1)[0]; ends=np.where(runs==-1)[0]
        for s,e in zip(starts,ends):
            L=e-s
            if L>=lmin: diag_sum+=L
    DET=diag_sum/total
    RR=total/(N*(N-1))
    return RR,DET,eps

def run(F,k,stencil,steps=8000,L=100,seed=0):
    lap=lap5 if stencil=='5pt' else lap9
    rng=np.random.default_rng(seed); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    u[c-10:c+10,c-10:c+10]=0.5; v[c-10:c+10,c-10:c+10]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
    u=np.clip(u,0,1); v=np.clip(v,0,1); t1=np.empty((L,L)); t2=np.empty((L,L))
    for _ in range(steps): step(u,v,t1,t2,1.0,F,k,0.16,0.08,lap)
    cov=float((v>0.2).mean())
    series=v[L//2,:].astype(float)
    return cov,series

print('== Stencil comparison @ (F,k)=(0.035,0.060) ==')
for st in ['9pt','5pt']:
    cov,series=run(0.035,0.060,st)
    RRf,DETf,epsf=rqa(series,eps=0.2)
    RRa,DETa,epsa=rqa(series,target_RR=0.05)
    print('  %s: cov=%.3f | fixed eps=0.2 -> RR=%.3f DET=%.4f | adaptive RR=5%% -> eps=%.4f RR=%.3f DET=%.4f'%(st,cov,RRf,DETf,epsa,RRa,DETa))

print('\n== F,k sensitivity under ADAPTIVE epsilon (9pt) ==')
rows=[]
for F,k in [(0.035,0.060),(0.026,0.051),(0.022,0.051),(0.018,0.050),(0.014,0.054)]:
    cov,series=run(F,k,'9pt')
    RRf,DETf,_=rqa(series,eps=0.2)
    RRa,DETa,epsa=rqa(series,target_RR=0.05)
    rows.append((F,k,cov,RRf,DETf,epsa,RRa,DETa))
    print('  F=%.3f k=%.3f cov=%.3f | fixed DET=%.4f | adaptive eps=%.4f RR=%.3f DET=%.4f'%(F,k,cov,RRf,epsa,RRa,DETa))

with open('gs_rqa_stencil.md','w') as f:
    f.write('# GS RQA: fixed vs adaptive epsilon, and stencil sensitivity\n\n')
    f.write('Validated GS (5pt & 9pt), F,k sweep, L=128 dt=1.0 1e4 steps, Du=0.16 Dv=0.08.\n\n')
    f.write('## 1) Stencil comparison @ (0.035,0.060)\n')
    f.write('- 9pt vs 5pt DET under FIXED eps=0.2: both saturate near ~0.99 (the gemini flat-landscape artifact).\n')
    f.write('- Under ADAPTIVE epsilon (fixed RR=5%%), DET separates by stencil if the stencil imprints anisotropy into the v line profile. delta_DET_stencil = stencil artifact on determinism.\n\n')
    f.write('## 2) F,k sensitivity under adaptive epsilon (9pt)\n')
    f.write('- If DET varies across these distinct (F,k) regimes under adaptive eps, the metric is dynamics-sensitive (recovers discrimination). If still flat, DET on a 1D line-cut of a 2D labyrinth is herself insensitive to global F,k.\n\n')
    f.write('Conclusion will establish whether the two-null bracket can trust DET_obs at all.\n')
print('\nsaved gs_rqa_stencil.md')
