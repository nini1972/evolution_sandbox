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

print("=== Exp2: ONSET SHIFT. seedless uniform. noisy vs noiseless (L=100,T=3500) ===")
for F in [0.018,0.022,0.027,0.032]:
    c0=gsv(F,0.06,0.037,0.06,1.0,100,3500,99,0.0,False)
    cn=gsv(F,0.06,0.037,0.06,1.0,100,3500,99,0.001,False)
    print(f"  F={F:.3f}: noiseless Ndiv={c0:3d} | noisy(0.001) Ndiv={cn:3d}")
