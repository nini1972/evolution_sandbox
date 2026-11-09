import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Pearson 1993 "self-replicating spots" regime (known to produce patterns)
F,k=0.046,0.063
Du,Dv=0.16,0.08
L,dt,T=160,1.0,6000

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
def step(u,v,t1,t2,applyf,dt):
    L=u.shape[0]
    for t in range(1):
        applyf(u,t1); applyf(v,t2)
        for y in range(L):
            for x in range(L):
                uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
                u[y,x]=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x])
                v[y,x]=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])

def run(applyf,seed):
    rng=np.random.default_rng(seed)
    u=np.ones((L,L)); v=np.zeros((L,L))
    # Pearson typical init: square of v=0.25 in center, plus tiny noise
    yy,xx=np.ogrid[:L,:L]
    sq=(np.abs(yy-L//2)<10)&(np.abs(xx-L//2)<10)
    v[sq]=0.25
    u+=rng.standard_normal((L,L))*0.01
    v+=rng.standard_normal((L,L))*0.01
    t1=np.empty((L,L)); t2=np.empty((L,L))
    for t in range(T):
        step(u,v,t1,t2,applyf,dt)
        if t%1000==0:
            print("  t=%4d u[min/max/mean]=%.3f/%.3f/%.3f v[min/mean/max]=%.4f/%.4f/%.4f"%(t,u.min(),u.max(),u.mean(),v.min(),v.mean(),v.max()))
        if not np.isfinite(u).all(): 
            print("  NaN at t=%d"%t); break
    return u,v

print("=== 5-pt Pearson F=0.046 k=0.063 ===")
u5,v5=run(lap5,7)
print("=== 9-pt Pearson F=0.046 k=0.063 ===")
u9,v9=run(lap9,7)

cv5=(v5>0.25).mean(); cv9=(v9>0.25).mean()
print("5-pt pattern-cover=%.3f  9-pt pattern-cover=%.3f"%(cv5,cv9))
fig,ax=plt.subplots(1,2,figsize=(10,5))
ax[0].imshow(u5,cmap='magma'); ax[0].set_title('Pearson 5-pt (should show spots)')
ax[1].imshow(u9,cmap='magma'); ax[1].set_title('Pearson 9-pt')
plt.tight_layout(); plt.savefig('pearson_test.png',dpi=110); plt.close()
print("DONE")
