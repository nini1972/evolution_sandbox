import numpy as np

def gray_scott(N=48,T=400,F=0.037,k=0.06,dt=0.4):
    u=np.ones((N,N)); v=np.zeros((N,N))
    r=N//20
    u[N//2-r:N//2+r,N//2-r:N//2+r]=0.5
    v[N//2-r:N//2+r,N//2-r:N//2+r]=0.25
    Du,Dv=0.16,0.08
    frames=[]
    for t in range(T):
        lap_u=u+np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)-4*u
        lap_v=v+np.roll(v,1,0)+np.roll(v,-1,0)+np.roll(v,1,1)+np.roll(v,-1,1)-4*v
        uvv=u*v*v
        u=u+dt*(Du*lap_u - uvv + F*(1-u))
        v=v+dt*(Dv*lap_v + uvv - (k+F)*v)
        np.clip(u,0,1,out=u); np.clip(v,0,1,out=v)
        if t>=T-40: frames.append((v>0.2).astype(int))
    frames=np.array(frames)
    return frames

for (F,k) in [(0.037,0.06),(0.022,0.051),(0.014,0.054)]:
    fr=gray_scott(F=F,k=k)
    cov=fr[-1].mean()
    print(f"F={F} k={k} final_coverage={cov:.3f} alive={fr[-1].any()}")
