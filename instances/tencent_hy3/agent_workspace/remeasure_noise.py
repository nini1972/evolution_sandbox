"""HONEST RE-MEASUREMENT (local, fast).
Re-derive the Gray-Scott mitosis-band NOISE optimum using the REAL detector
(division_count = # mid-size B-components, 20-200 px, B>0.25) and the CORRECT
band core k (not the false 0.0603 used by the broken verifier).
Also re-probe the band center at F=0.040 with correct k-window to confirm band.
"""
import numpy as np, json, time
try:
    from numba import njit
    HAVE_NJIT = True
except Exception:
    HAVE_NJIT = False
from scipy.ndimage import label

@njit(cache=True)
def gs_step(A, B, Da, Db, F, k, dt, noiseA, noiseB):
    N = A.shape[0]
    An = A.copy(); Bn = B.copy()
    for i in range(N):
        for j in range(N):
            im=(i-1+N)%N; ip=(i+1)%N; jm=(j-1+N)%N; jp=(j+1)%N
            lapA = A[im,j]+A[ip,j]+A[i,jm]+A[i,jp]-4.0*A[i,j]
            lapB = B[im,j]+B[ip,j]+B[i,jm]+B[i,jp]-4.0*B[i,j]
            abb = A[i,j]*B[i,j]*B[i,j]
            An[i,j] = A[i,j] + (Da*lapA - abb + F*(1.0-A[i,j]) + noiseA[i,j])*dt
            Bn[i,j] = B[i,j] + (Db*lapB + abb - (k+F)*B[i,j] + noiseB[i,j])*dt
    return An, Bn

def simulate(F, k, Da=0.16, Db=0.08, N=96, steps=10000, dt=1.0, sigma=0.0, rng=None):
    A = np.ones((N,N)); B = np.zeros((N,N))
    r=10; A[N//2-r:N//2+r, N//2-r:N//2+r]=0.5; B[N//2-r:N//2+r, N//2-r:N//2+r]=0.25
    for t in range(steps):
        if sigma>0:
            na = rng.normal(0, sigma, (N,N)); nb = rng.normal(0, sigma, (N,N))
        else:
            na = np.zeros((N,N)); nb = np.zeros((N,N))
        if HAVE_NJIT:
            A,B = gs_step(A,B,Da,Db,F,k,dt,na,nb)
        else:
            lapA = A + np.roll(A,1,0)+np.roll(A,-1,0)+np.roll(A,1,1)+np.roll(A,-1,1)-5*A
            lapB = B + np.roll(B,1,0)+np.roll(B,-1,0)+np.roll(B,1,1)+np.roll(B,-1,1)-5*B
            abb = A*B*B
            A = A + (Da*lapA - abb + F*(1-A) + na)*dt
            B = B + (Db*lapB + abb - (k+F)*B + nb)*dt
        A=np.clip(A,0,1); B=np.clip(B,0,1)
    return A,B

def division_count(B, lo=20, hi=200, thr=0.25):
    lab,n = label(B>thr)
    if n==0: return 0.0
    sizes = np.bincount(lab.ravel())[1:]
    return float(np.sum((sizes>=lo)&(sizes<=hi)))

t0=time.time()
# (A) Confirm band center at F=0.040 with CORRECT k-window [0.060,0.067]
F=0.040; ks=np.round(np.arange(0.060,0.0671,0.0005),6)
band=[]
for k in ks:
    rng=np.random.default_rng(2024)
    A,B=simulate(F,k,rng=rng); nd=division_count(B)
    band.append((float(k),nd)); print(f"  F={F} k={k:.4f} Ndiv={nd:.0f} t={time.time()-t0:.0f}s")
band=np.array(band); kp=band[np.argmax(band[:,1])]
print(f"  => REAL band peak F=0.040 at k={kp[0]:.4f} Nmax={kp[1]:.0f}")

# (B) Noise robustness at the CORRECT band core (k=0.0647, near F=0.040 peak)
sigmas=[0.0,0.002,0.005,0.01,0.02,0.03,0.05]
noise=[]
kcore=0.0647
for sig in sigmas:
    vals=[]
    for sd in (11,22):
        rng=np.random.default_rng(sd)
        A,B=simulate(0.040,kcore,sigma=sig,rng=rng); vals.append(division_count(B))
    nv=float(np.mean(vals)); noise.append((sig,nv)); print(f"  sigma={sig:.3f} Ndiv={nv:.1f} (n=2) t={time.time()-t0:.0f}s")

out={'F_band':0.040,'band_ks':band[:,0].tolist(),'band_Ndiv':band[:,1].tolist(),
     'band_peak_k':float(kp[0]),'band_peak_N':float(kp[1]),
     'noise_kcore':kcore,'noise_sigmas':[s for s,_ in noise],'noise_Ndiv':[n for _,n in noise],
     'elapsed_s':time.time()-t0}
json.dump(out, open('remeasure_noise.json','w'), indent=1)
print("WROTE remeasure_noise.json")
print("DONE t=%.0fs"%(time.time()-t0))
