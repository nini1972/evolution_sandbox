import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
W_E,W_C=0.2,0.05
@njit(cache=True)
def lap(u,L):
    out=np.empty_like(u)
    for y in range(L):
        for x in range(L):
            out[y,x]=-u[y,x]+W_E*(u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L])+W_C*(u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L])
    return out
@njit(cache=True)
def run(u,v,a,b,Du,Dv,dt,L,T):
    for t in range(T):
        Lu=lap(u,L); Lv=lap(v,L)
        for y in range(L):
            for x in range(L):
                uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
                u[y,x]=uu+dt*(a-uu+u2v+Du*Lu[y,x])
                v[y,x]=vv+dt*(b-u2v+Dv*Lv[y,x])
L=120; dt=0.02; T=3000; a,b,Du,Dv=0.8,0.6,0.05,2.0
np.random.seed(0)
u=np.full((L,L),a)+np.random.normal(0,1e-3,(L,L))
v=np.full((L,L),b/(a*a))+np.random.normal(0,1e-3,(L,L))
run(u,v,a,b,Du,Dv,dt,L,T)
fig,ax=plt.subplots(1,2,figsize=(8,4))
ax[0].imshow(v,cmap='magma'); ax[0].set_title('Schnakenberg final v (flat)')
ax[1].text(0.5,0.5,f'v-std = {v.std():.2e}\n(no pattern)\na={a} b={b}\nDu={Du} Dv={Dv}',ha='center',va='center',transform=ax[1].transAxes,fontsize=14)
ax[1].axis('off')
fig.suptitle('Schnakenberg: NO void-genesis (corrected kernel)')
fig.tight_layout(); fig.savefig('honest_schnakenberg.png',dpi=100); plt.close()
print('v-std',v.std())
