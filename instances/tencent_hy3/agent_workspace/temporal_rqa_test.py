import numpy as np
from numba import njit

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=(4.0*orth+1.0*diag-20.0*u[y,x])/6.0

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
    ds=0
    for k in range(1,N):
        d=np.diag(R,k).astype(int)
        if d.sum()==0: continue
        runs=np.diff(np.concatenate(([0],d,[0])))
        for s,e in zip(np.where(runs==1)[0],np.where(runs==-1)[0]):
            if e-s>=lmin: ds+=e-s
    return total/(N*(N-1)), ds/total, eps

# TEMPORAL series: v at center point over time (smooth, low-dimensional)
L=96; trans=2000; rec=2000; F,k=0.035,0.060
rng=np.random.default_rng(0); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
u[c-10:c+10,c-10:c+10]=0.5; v[c-10:c+10,c-10:c+10]=0.25
u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
u=np.clip(u,0,1); v=np.clip(v,0,1); t1=np.empty((L,L)); t2=np.empty((L,L)); lap=lap9
for _ in range(trans): step(u,v,t1,t2,1.0,F,k,0.16,0.08,lap)
ts=[]
for _ in range(rec):
    step(u,v,t1,t2,1.0,F,k,0.16,0.08,lap); ts.append(v[c,c])
ts=np.array(ts)
RRf,DETf,_=rqa(ts,eps=0.2)
RRaz,DETaz,epsaz=rqa(ts,target_RR=0.05)
print('TEMPORAL v(c) series (smooth): fixed eps=0.2 -> RR=%.3f DET=%.4f | adaptive RR5%% -> eps=%.5f RR=%.3f DET=%.4f'%(RRf,DETf,epsaz,RRaz,DETaz))
print('=> if DETf~0.999/1.0, fixed-eps saturation on TEMPORAL GS series is the 0.999 mechanism (not z-score).')
