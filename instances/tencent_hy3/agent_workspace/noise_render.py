import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

@njit(cache=True)
def gsv_field(F,k,Du,Dv,dt,L,T,seed,sigma):
    u=np.ones((L,L)); v=np.zeros((L,L))
    for cy in range(3):
        for cx in range(3):
            a=int(L*(cx+1)/4); b=int(L*(cy+1)/4)
            u[a:a+int(L/10), b:b+int(L/10)]=0.5; v[a:a+int(L/10), b:b+int(L/10)]=0.25
    lap=np.empty_like(u)
    np.random.seed(seed)
    for t in range(T):
        for x in range(L):
            for y in range(L):
                lap[x,y]=u[(x+1)%L,y]+u[(x-1)%L,y]+u[x,(y+1)%L]+u[x,(y-1)%L]-4*u[x,y]
        for i in range(L*L):
            x=i//L; y=i%L
            uvv=u[x,y]*v[x,y]*v[x,y]
            u[x,y]+=(Du*lap[x,y]-uvv+F*(1-u[x,y]))*dt
            v[x,y]+=(Dv*lap[x,y]+uvv-(F+k)*v[x,y])*dt
        if sigma>0:
            for i in range(L*L):
                u[i//L,i%L]+=np.random.standard_normal()*sigma
                v[i//L,i%L]+=np.random.standard_normal()*sigma
    return v

def count(v):
    L=v.shape[0]; visited=np.zeros((L,L),np.int8); cl=0
    for i in range(L*L):
        x=i//L;y=i%L
        if v[x,y]>0.1 and visited[x,y]==0:
            cl+=1;st=[(x,y)]
            while st:
                cx,cy=st.pop()
                for dx in(-1,0,1):
                    for dy in(-1,0,1):
                        nx=(cx+dx)%L;ny=(cy+dy)%L
                        if v[nx,ny]>0.1 and visited[nx,ny]==0:
                            visited[nx,ny]=1;st.append((nx,ny))
    return cl

# Panels: noiseless, constructive, annihilation
fig,axs=plt.subplots(1,3,figsize=(13,4.2))
for ax,(s,lab) in zip(axs,[(0.0,'noiseless (sigma=0)'),(0.0005,'constructive (sigma=0.0005)'),(0.002,'annihilated (sigma=0.002)')]):
    v=gsv_field(0.036,0.06,0.037,0.06,1.0,100,3000,42,s)
    ax.imshow(v,vmin=0,vmax=0.6,cmap='magma'); ax.set_title(f'{lab}\nN_div={count(v)}'); ax.axis('off')
plt.suptitle('Gray-Scott V-morphology under increasing stochastic forcing (F=0.036, k=0.06)')
plt.tight_layout(); plt.savefig('pattern_noise.png',dpi=120); print('saved pattern_noise.png')

# Robustness across seeds at F=0.036
print("=== robustness: F=0.036, sigma=0 vs 0.0003 across seeds ===")
for seed in [7,13,99]:
    c0=count(gsv_field(0.036,0.06,0.037,0.06,1.0,100,3000,seed,0.0))
    c1=count(gsv_field(0.036,0.06,0.037,0.06,1.0,100,3000,seed,0.0003))
    print(f"  seed={seed}: noiseless={c0} constructive={c1}")
