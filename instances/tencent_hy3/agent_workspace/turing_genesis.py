import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

@njit(cache=True)
def schnakenberg(a,b,Du,Dv,dt,L,T,seed,sigma0,noise_each):
    # homogeneous fixed point
    u=np.ones((L,L))*(a+b)
    v=np.ones((L,L))*(b/((a+b)**2))
    np.random.seed(seed)
    # initial perturbation
    for i in range(L*L):
        u[i//L,i%L]+=np.random.standard_normal()*sigma0
        v[i//L,i%L]+=np.random.standard_normal()*sigma0
    lapu=np.empty_like(u); lapv=np.empty_like(v)
    for t in range(T):
        for x in range(L):
            for y in range(L):
                lapu[x,y]=u[(x+1)%L,y]+u[(x-1)%L,y]+u[x,(y+1)%L]+u[x,(y-1)%L]-4*u[x,y]
                lapv[x,y]=v[(x+1)%L,y]+v[(x-1)%L,y]+v[x,(y+1)%L]+v[x,(y-1)%L]-4*v[x,y]
        for i in range(L*L):
            x=i//L; y=i%L
            uv=u[x,y]*u[x,y]*v[x,y]
            u[x,y]+=(Du*lapu[x,y] + a - u[x,y] + uv)*dt
            v[x,y]+=(Dv*lapv[x,y] + b - uv)*dt
        if noise_each:
            for i in range(L*L):
                u[i//L,i%L]+=np.random.standard_normal()*noise_each
                v[i//L,i%L]+=np.random.standard_normal()*noise_each
    return u,v

# Turing-unstable params (Dv/Du=10): classic spot/stripe genesis
a,b,Du,Dv,dt,L,T=(0.1,0.9,0.01,0.1,0.2,120,20000)

print("=== GENESIS FROM VOID: Schnakenberg Turing patterns ===")
# 1) truly noiseless: stays uniform (no form)
u0,v0=schnakenberg(a,b,Du,Dv,dt,L,T,42,0.0,0.0)
print(f"  noiseless:  u std={u0.std():.4f}  v std={v0.std():.4f}  (std~0 => VOID, no form)")
# 2) seed once with infinitesimal noise, then silent: Turing growth
u1,v1=schnakenberg(a,b,Du,Dv,dt,L,T,42,1e-4,0.0)
print(f"  seed-noise only: u std={u1.std():.4f}  v std={v1.std():.4f}  (Turing GROWTH => form)")
# 3) continuous tiny noise (fluctuation-driven genesis)
u2,v2=schnakenberg(a,b,Du,Dv,dt,L,T,42,1e-4,1e-4)
print(f"  cont-noise: u std={u2.std():.4f}  v std={v2.std():.4f}")

# render
fig,axs=plt.subplots(1,3,figsize=(13,4.2))
axs[0].imshow(v0,cmap='magma'); axs[0].set_title('Noiseless void\n(uniform, no form)'); axs[0].axis('off')
axs[1].imshow(v1,cmap='magma'); axs[1].set_title('Seed-noise (1e-4) once\n=> Turing spots emerge'); axs[1].axis('off')
axs[2].imshow(v2,cmap='magma'); axs[2].set_title('Continuous noise\n=> sustained pattern'); axs[2].axis('off')
plt.suptitle('Lamb from Lion: Genesis of Form from a Uniform Void via Turing Instability (Schnakenberg)')
plt.tight_layout(); plt.savefig('turing_genesis.png',dpi=120); print('saved turing_genesis.png')
