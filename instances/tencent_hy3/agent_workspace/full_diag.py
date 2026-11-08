import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

F,k=0.0739,0.0620
Du,Dv=0.16,0.08
L,dt,T=128,1.0,4000

disc=1.0-4.0*(F+k)**2/F
us=0.5*(1.0-np.sqrt(disc)); vs=(F+k)/us
print("Interior FP u*=%.4f v*=%.4f"%(us,vs))

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*u[y,x]+1.0*orth+0.25*diag

@njit
def step(u,v,tmp,T):
    L=u.shape[0]
    for t in range(T):
        lap9(u,tmp); Lu=tmp.copy()
        lap9(v,tmp); Lv=tmp.copy()
        for y in range(L):
            for x in range(L):
                uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
                u[y,x]=uu+dt*(F*(1.0-uu)-u2v+Du*Lu[y,x])
                v[y,x]=vv+dt*(u2v-(F+k)*vv+Dv*Lv[y,x])

# seed: noise on FP + a localized blob to break symmetry strongly
rng=np.random.default_rng(5)
u=np.full((L,L),us)+rng.standard_normal((L,L))*0.05
v=np.full((L,L),vs)+rng.standard_normal((L,L))*0.05
cy,cx=L//2,L//2
yy,xx=np.ogrid[:L,:L]
blob=(yy-cy)**2+(xx-cx)**2<25
u[blob]=0.9; v[blob]=0.3
print("init u mean=%.3f v mean=%.3f"%(u.mean(),v.mean()))

tmp=np.empty((L,L))
snaps={}
for t in range(T):
    step(u,v,tmp,1)
    if t%500==0 or t==T-1:
        print("t=%4d  u[min/max/mean]=%.3f/%.3f/%.3f  v[min/mean/max]=%.4f/%.4f/%.4f"%(t,u.min(),u.max(),u.mean(),v.min(),v.mean(),v.max()))
        if t in (1000,2000,3000,3999):
            plt.imsave("snap_t%d.png"%(t+1),u,cmap='magma')

np.save("final_u.npy",u)
print("FINAL u[min/max/mean]=%.4f/%.4f/%.4f  v std=%.5f  NaN=%s"%(u.min(),u.max(),u.mean(),v.std(),np.isnan(u).any()))
# pattern coverage
print("pattern cover (v>0.25)=%.3f"%(v>0.25).mean())
