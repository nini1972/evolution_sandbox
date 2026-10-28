import numpy as np
from numba import njit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

@njit(cache=True)
def gsv(F,k,Du,Dv,dt,L,T,seed,sigma):
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
    visited=np.zeros((L,L),np.int8); clusters=0
    for i in range(L*L):
        x=i//L; y=i%L
        if v[x,y]>0.1 and visited[x,y]==0:
            clusters+=1; st=[(x,y)]
            while st:
                cx,cy=st.pop()
                for dx in(-1,0,1):
                    for dy in(-1,0,1):
                        nx=(cx+dx)%L; ny=(cy+dy)%L
                        if v[nx,ny]>0.1 and visited[nx,ny]==0:
                            visited[nx,ny]=1; st.append((nx,ny))
    return clusters

sigmas=np.array([0.0,0.0003,0.0005,0.0007,0.001,0.0015,0.002,0.003,0.005,0.01])
Fvals=[0.036,0.04]
colors=['#2c7fb8','#d95f0e']
plt.figure(figsize=(8,5))
for Fi,c in zip(Fvals,colors):
    ndiv=[gsv(Fi,0.06,0.037,0.06,1.0,100,3000,42,s) for s in sigmas]
    plt.plot(sigmas,ndiv,marker='o',color=c,label=f'F={Fi}')
    print(f"F={Fi}:",list(zip(sigmas,ndiv)))
plt.axvspan(0.0005,0.001,color='green',alpha=0.12,label='constructive band')
plt.axvline(0.003,color='red',ls='--',alpha=0.6,label='annihilation threshold')
plt.xlabel('noise amplitude sigma'); plt.ylabel('structural diversity (N_div, # V-clusters)')
plt.title('Constructive Noise Band in Gray-Scott Spotted Regime\n(small stochastic forcing IGNITES/ENRICHES; large destroys)')
plt.legend(); plt.yscale('symlog'); plt.tight_layout()
plt.savefig('noise_band.png',dpi=130); print("saved noise_band.png")
