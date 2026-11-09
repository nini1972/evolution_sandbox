import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json

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

def run(applyf,F,k,Du,Dv,seed,L=160,dt=0.5,T=8000):
    rng=np.random.default_rng(seed)
    u=np.ones((L,L)); v=np.zeros((L,L))
    yy,xx=np.ogrid[:L,:L]
    sq=(np.abs(yy-L//2)<12)&(np.abs(xx-L//2)<12)
    u[sq]=0.5; v[sq]=0.25           # canonical Pearson seed
    u+=rng.standard_normal((L,L))*0.005
    v+=rng.standard_normal((L,L))*0.005
    t1=np.empty((L,L)); t2=np.empty((L,L))
    last=None
    for t in range(T):
        step(u,v,t1,t2,applyf,dt,F,k,Du,Dv)
        if not np.isfinite(u).all():
            print("  NaN at t=%d"%t); break
    return u,v

def report(name,u,v):
    cv=(v>0.25).mean()
    print("%-26s u[%.3f/%.3f/%.3f] v_std=%.4f cover=%.3f NaN=%s"%(name,u.min(),u.max(),u.mean(),v.std(),cv,np.isnan(u).any()))
    return dict(name=name,u_min=float(u.min()),u_max=float(u.max()),u_mean=float(u.mean()),
                v_std=float(v.std()),pattern_cover=float(cv),NaN=bool(np.isnan(u).any())) if not np.isnan(u).any() else None

Du,Dv=0.16,0.08
results={}
# 1) Pearson known spots regime
print("--- Pearson F=0.046 k=0.063 (expect spots) ---")
u5,v5=run(lap5,0.046,0.063,Du,Dv,7); 
u9,v9=run(lap9,0.046,0.063,Du,Dv,7)
r5=report("Pearson 5-pt",u5,v5); r9=report("Pearson 9-pt",u9,v9)
results['pearson']=dict(p5=r5,p9=r9)
plt.imsave("pearson_5pt.png",u5,cmap='magma'); plt.imsave("pearson_9pt.png",u9,cmap='magma')

# 2) My Turing params F=0.0739 k=0.0620
print("--- Mine F=0.0739 k=0.0620 (Turing-predicted) ---")
u5b,v5b=run(lap5,0.0739,0.0620,Du,Dv,7)
u9b,v9b=run(lap9,0.0739,0.0620,Du,Dv,7)
rb5=report("Mine 5-pt",u5b,v5b); rb9=report("Mine 9-pt",u9b,v9b)
results['mine']=dict(p5=rb5,p9=rb9)
plt.imsave("mine_5pt.png",u5b,cmap='magma'); plt.imsave("mine_9pt.png",u9b,cmap='magma')

json.dump(results,open('robust_results.json','w'),indent=2,default=lambda o:None)
print("DONE")
