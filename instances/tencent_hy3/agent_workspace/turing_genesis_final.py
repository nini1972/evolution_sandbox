import numpy as np, time
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def lap(A):  # periodic Laplacian via roll
    return (np.roll(A,1,0)+np.roll(A,-1,0)+np.roll(A,1,1)+np.roll(A,-1,1)-4*A)

def schnak(a,b,Du,Dv,dt,L,T,seed,sigma0,noise_each):
    rng=np.random.default_rng(seed)
    u=np.ones((L,L))*(a+b); v=np.ones((L,L))*(b/((a+b)**2))
    u+=rng.standard_normal((L,L))*sigma0; v+=rng.standard_normal((L,L))*sigma0
    for t in range(T):
        uv=u*u*v
        u+= (Du*lap(u)+a-u+uv)*dt
        v+= (Dv*lap(v)+b-uv)*dt
        if noise_each>0:
            u+=rng.standard_normal((L,L))*noise_each
            v+=rng.standard_normal((L,L))*noise_each
    return u,v

a,b,Du,Dv,dt,L=(0.1,0.9,0.01,0.1,0.2,100)
print("=== GENESIS THRESHOLD SCAN (T=12000) ===")
for label,sig,na in [("noiseless",0,0),("seed1e-2",1e-2,0),("cont1e-5",1e-4,1e-5),("cont1e-4",1e-4,1e-4),("cont1e-3",1e-4,1e-3)]:
    t0=time.time(); u,v=schnak(a,b,Du,Dv,dt,L,12000,42,sig,na); dt_=time.time()-t0
    print(f"  {label:10s}: v std={v.std():.5f}  -> {'FORM' if v.std()>0.01 else 'void'}  ({dt_:.1f}s)")

# good render: continuous noise genesis
u,v=schnak(a,b,Du,Dv,dt,L,14000,42,1e-4,1e-4)
# also noiseless for contrast
u0,v0=schnak(a,b,Du,Dv,dt,L,14000,42,0,0)
fig,axs=plt.subplots(1,2,figsize=(9,4.2))
axs[0].imshow(v0,cmap='magma'); axs[0].set_title('Noiseless void\n(no form)'); axs[0].axis('off')
axs[1].imshow(v,cmap='magma'); axs[1].set_title('Continuous micro-noise (σ=1e-4)\n=> Turing pattern emerges'); axs[1].axis('off')
plt.suptitle('Genesis of Form from the Void: Lamb from Lion (Schnakenberg RD)')
plt.tight_layout(); plt.savefig('turing_genesis.png',dpi=130)
print("saved turing_genesis.png; formed v std=%.4f"%v.std())
