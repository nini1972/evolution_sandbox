import numpy as np, sys
from numba import njit
sys.path.insert(0,'.')
from brusselator_test4 import bruss_step

a,b,Du,Dv=0.8,1.6,0.05,1.0
L=90; dt=0.02
print("=== multi-seed genesis robustness (pure noise -> pattern?) ===")
results=[]
for seed in range(6):
    np.random.seed(seed)
    u=np.full((L,L),a); v=np.full((L,L),b/a)
    u+=np.random.normal(0,1e-3,(L,L)); v+=np.random.normal(0,1e-3,(L,L))
    for t in range(10000):
        bruss_step(u,v,a,b,Du,Dv,dt,L)
    f=v-v.mean()
    F=np.fft.fft2(f); P=np.abs(np.fft.fftshift(F))**2
    cy,cx=P.shape[0]//2,P.shape[1]//2; P[cy,cx]=0
    ky,kx=np.unravel_index(np.argmax(P),P.shape); k=np.sqrt((ky-cy)**2+(kx-cx)**2)*2*np.pi/L
    gen = f.std()>0.05 and P.max()>np.abs(F[cy,cx])**2*5
    results.append(gen)
    print(f"  seed={seed}: vstd={f.std():.4f} |k|peak={k:.2f}  GENESIS={'YES' if gen else 'no'}")
print(f"\nGenesis occurred in {sum(results)}/{len(results)} seeds (pure-noise initial condition).")
