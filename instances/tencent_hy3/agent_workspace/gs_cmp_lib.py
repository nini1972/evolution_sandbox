import numpy as np, time
from numba import njit
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
try:
    from colony_lib.dynamics import GrayScott2D, simulate_gray_scott
    HAVE=True
except Exception as e:
    HAVE=False; print('no colony_lib', e)

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]
@njit
def step(u,v,t1,t2,dt,F,k,Du,Dv):
    L=u.shape[0]; lap5(u,t1); lap5(v,t2)
    for y in range(L):
        for x in range(L):
            uu=u[y,x]; vv=v[y,x]; u2v=uu*uu*vv
            nu=uu+dt*(F*(1.0-uu)-u2v+Du*t1[y,x]); nv=vv+dt*(u2v-(F+k)*vv+Dv*t2[y,x])
            u[y,x]=0.0 if nu<0 else (1.0 if nu>1 else nu); v[y,x]=0.0 if nv<0 else (1.0 if nv>1 else nv)

def seed_square(L,r,sn):
    rng=np.random.default_rng(sn); u=np.ones((L,L)); v=np.zeros((L,L)); c=L//2
    u[c-r:c+r, c-r:c+r]=0.5; v[c-r:c+r, c-r:c+r]=0.25
    u+=rng.uniform(-0.05,0.05,size=(L,L)); v+=rng.uniform(-0.05,0.05,size=(L,L))
    return np.clip(u,0,1),np.clip(v,0,1)

F,k,L,T,dt=0.035,0.060,128,10000,1.0
print('Ground-truth comparison (F=%.3f k=%.3f dt=%g steps=%d, SQUARE seed r=10):'%(F,k,dt,T))
# A. colony_lib GrayScott2D
if HAVE:
    sim=GrayScott2D(grid_size=L, Du=0.16, Dv=0.08, F=F, k=k, dt=dt); sim.seed_center(radius=10, seed=42); sim.integrate(steps=T)
    vA=sim.v; print('  A) colony_lib GrayScott2D : std_v=%.4f mean_v=%.4f cover=%.3f'%(vA.std(),vA.mean(), float((vA>0.2).mean())))
    plt.figure(figsize=(4,4)); plt.imshow(vA,cmap='magma'); plt.title('A: colony_lib'); plt.axis('off'); plt.tight_layout(); plt.savefig('cmp_A_lib.png',dpi=90); plt.close()
# B. my handwritten, identical square seed & params
u0,v0=seed_square(L,10,42)
u,v=u0.copy(),v0.copy(); t1=np.empty((L,L)); t2=np.empty((L,L))
t0=time.time()
for _ in range(T): step(u,v,t1,t2,dt,F,k,0.16,0.08)
print('  B) my handwritten 5pt   : std_v=%.4f mean_v=%.4f cover=%.3f (%.1fs)'%(v.std(),v.mean(), float((v>0.2).mean()), time.time()-t0))
plt.figure(figsize=(4,4)); plt.imshow(v,cmap='magma'); plt.title('B: my 5pt'); plt.axis('off'); plt.tight_layout(); plt.savefig('cmp_B_mine.png',dpi=90); plt.close()
print('saved cmp_A_lib.png, cmp_B_mine.png')
