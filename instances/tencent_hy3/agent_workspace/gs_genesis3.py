import numpy as np, time, sys
from numba import njit
sys.path.insert(0,'.')
from gs_step import gs_step
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

@njit(cache=True)
def random_ic(L,seed):
    np.random.seed(seed)
    u=np.empty((L,L)); v=np.empty((L,L))
    for i in range(L*L):
        u[i//L,i%L]=0.5 + np.random.random()*0.5
        v[i//L,i%L]=0.0 + np.random.random()*0.3
    return u,v

Du,Dv,dt,L=0.037,0.06,1.0,90
F,k=0.034,0.061
u,v=random_ic(L,7)
snaps=[]
for step in range(100000):
    gs_step(u,v,F,k,Du,Dv,dt,L)
    if step%10000==0 or step==99999:
        snaps.append((step,v.copy()))
        print(f"  step={step} vmean={v.mean():.4f} vmax={v.max():.3f} frac>0.1={(v>0.1).mean():.4f}")
fig,ax=plt.subplots(1,len(snaps),figsize=(3*len(snaps),3))
for a,(s,im) in zip(ax,snaps):
    a.imshow(im,vmin=0,vmax=0.4,cmap='magma'); a.set_title(f"t={s//1000}k"); a.axis('off')
fig.savefig('gs_genesis_long.png',dpi=90); print("saved gs_genesis_long.png")
