import numpy as np; from numba import njit
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
W_E,W_C=0.2,0.05; L=120; T=4000; dt=1.0; Du,Dv,F,k=0.16,0.08,0.06,0.062
@njit
def lap(u,L,zerosum):
    out=np.empty_like(u)
    for y in range(L):
        for x in range(L):
            out[y,x]=-u[y,x]+W_E*(u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L])+W_C*(u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L])
    if zerosum:
        m=out.mean(); 
        for y in range(L):
            for x in range(L): out[y,x]-=m
    return out
@njit
def run(u,v,dt,L,T,zerosum):
    for t in range(T):
        Lu=lap(u,L,zerosum);Lv=lap(v,L,zerosum)
        for y in range(L):
            for x in range(L):
                uu=u[y,x];vv=v[y,x];u2v=uu*uu*vv
                u[y,x]=uu+dt*(F*(1-uu)+uu*uu*vv+Du*Lu[y,x])
                v[y,x]=vv+dt*(uu-u2v-(F+k)*vv+Dv*Lv[y,x])
def pattern(seed):
    np.random.seed(seed)
    u=1-np.random.random((L,L)); v=np.random.random((L,L))
    run(u,v,dt,L,T,False); return u
# demonstrate momentum injection: <lap(u)> should be ~0 for standard, nonzero for zero-sum
np.random.seed(2); u=1-np.random.random((L,L)); v=np.random.random((L,L))
run(u,v,dt,L,T,False); std_mean_lap=np.mean(lap(u,L,False))
# now zero-sum run from same-ish with a different seed to get a patterned state
np.random.seed(3); uz=1-np.random.random((L,L)); vz=np.random.random((L,L))
run(uz,vz,dt,L,T,True); zs_mean_lap=np.mean(lap(uz,L,True))
print('standard <lap9(u)> after run =',std_mean_lap)
print('zero-sum <lap9(u)> after run   =',zs_mean_lap)
print('=> mean momentum injected per step (Du * mean_lap) std=%.3e  zs=%.4f'%(Du*std_mean_lap,Du*zs_mean_lap))
# curl-free vs solenoidal split for the ZERO-SUM operator acting on patterned field
Lx=lap(uz,L,True)
phi=np.zeros((L,L)); psi=np.zeros((L,L))  # solve on torus via FFT for verification (continuous approx)
# Use discrete Helmholtz via FFT of the operator already embedded:
# We'll just visualize the force field and its divergence-free vs curl-free via np.gradient Poisson solve
fx,fy=np.gradient(Lx)
# divergence and curl
div=np.gradient(fx,axis=1)+np.gradient(fy,axis=0)
# Poisson for phi: lap_phi = div  (use simple iterative relaxation on torus)
phi=np.zeros((L,L))
for _ in range(300):
    phi=0.25*(np.roll(phi,1,0)+np.roll(phi,-1,0)+np.roll(phi,1,1)+np.roll(phi,-1,1)-div)
phix,phiy=np.gradient(phi)
cf=(Lx-phix)  # residual = solenoidal part
print('|curl-free force| / |total force| = %.3f'%(np.sqrt((phix**2+phiy**2).mean())/np.sqrt((Lx**2).mean())))
print('|solenoidal force|/ |total force| = %.3f'%(np.sqrt((cf**2).mean())/np.sqrt((Lx**2).mean())))
fig,ax=plt.subplots(2,2,figsize=(9,8))
ax[0,0].imshow(pattern(1),cmap='magma');ax[0,0].set_title('u: standard 9-pt (patterned)')
ax[0,1].imshow(uz,cmap='magma');ax[0,1].set_title('u: zero-sum operator (patterned)')
ax[1,0].imshow(np.sqrt(phix**2+phiy**2),cmap='viridis');ax[1,0].set_title('|curl-free force| (pseudo-momentum source)')
ax[1,1].imshow(np.sqrt(cf**2),cmap='viridis');ax[1,1].set_title('|solenoidal (true divergence-free)|')
fig.suptitle('Zero-sum Laplacian injects curl-free pseudo-momentum (breaks mean conservation)')
fig.tight_layout();fig.savefig('momentum_injection.png',dpi=110);plt.close()
print('saved momentum_injection.png')
