import numpy as np
from numba import njit

@njit(cache=True)
def gsv(F,k,Du,Dv,dt,L,T,seed,sigma,seeded):
    u=np.ones((L,L)); v=np.zeros((L,L))
    if seeded:
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

import time
print("=== timing: L=120, T=4000 seeded F=0.04 ===")
t0=time.time(); c=gsv(0.04,0.06,0.16,0.08,1.0,120,4000,42,0.0,True); print("  Ndiv=",c,"time",round(time.time()-t0,1))
print("=== A: RESPONSIVENESS at funnel F=0.04,k=0.06 (seeded) ===")
for s in [0.0,0.01,0.03]:
    c=gsv(0.04,0.06,0.16,0.08,1.0,120,4000,42,s,True)
    print(f"  sigma={s}: Ndiv={c}")

print("=== B: NOISE-INDUCED ONSET, seedless uniform, F=0.025,k=0.06 (below threshold) ===")
for s in [0.0,0.005,0.02,0.05]:
    c=gsv(0.025,0.06,0.16,0.08,1.0,120,5000,99,s,False)
    print(f"  sigma={s}: Ndiv={c}")
