"""Fine cross-section + noise-robustness of the Gray-Scott mitosis band.
Continuous order parameter = 'division count' Ndiv = number of connected
B-components (B>0.25) whose area lies in a mid-range band.
Uses RELATIVE output dir 'world_c_results/' (per World C bridge contract).
"""
import os, numpy as np, json, time
OUTDIR = 'world_c_results'
os.makedirs(OUTDIR, exist_ok=True)
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

def simulate(F, k, Da=0.16, Db=0.08, N=96, steps=10000, dt=1.0, seed='center', sigma=0.0, rng=None):
    A = np.ones((N,N)); B = np.zeros((N,N))
    if seed=='center':
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

Fs = [0.030, 0.035, 0.040, 0.045]
ks = np.round(np.arange(0.0570, 0.0685+1e-9, 0.00025), 6)
cross = {}
t0=time.time()
for F in Fs:
    rng = np.random.default_rng(999)
    scores=[]
    for k in ks:
        A,B = simulate(F, k, N=96, steps=10000, seed='center', sigma=0.0, rng=rng)
        d = division_count(B)
        scores.append(d)
        print(f"F={F:.3f} k={k:.4f} Ndiv={d:.1f}")
    cross[str(F)] = {'ks':list(map(float,ks)), 'Ndiv':scores}
print(f"cross-section done t={time.time()-t0:.1f}s")

sigmas = [0.0, 0.002, 0.005, 0.01, 0.03, 0.05]
noise_tab = {}
for sig in sigmas:
    rng = np.random.default_rng(int(sig*1e5)+7)
    A,B = simulate(0.040, 0.063, N=96, steps=10000, seed='center', sigma=sig, rng=rng)
    noise_tab[str(sig)] = division_count(B)
    print(f"sigma={sig:.3f} Ndiv={noise_tab[str(sig)]:.1f}")
print("noise done")

out = {'Fs':Fs,'ks':list(map(float,ks)),'cross':cross,
       'noise_sigmas':list(map(float,sigmas)),'noise_Ndiv':noise_tab}
json.dump(out, open(os.path.join(OUTDIR,'gs_band_fine.json'),'w'), indent=1)

import matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(13,4.8))
for F in Fs:
    axes[0].plot(cross[str(F)]['ks'], cross[str(F)]['Ndiv'], label=f'F={F}')
axes[0].axvspan(0.063,0.065,color='green',alpha=0.15,label='band core')
axes[0].set_xlabel('k'); axes[0].set_ylabel('division count Ndiv (mid-size components)')
axes[0].set_title('Gray-Scott mitosis band: fine k cross-section'); axes[0].legend(); axes[0].grid(alpha=0.3)
sigs=[float(s) for s in noise_tab]; nvs=[noise_tab[s] for s in noise_tab]
axes[1].semilogx(sigs, nvs,'o-'); axes[1].set_xlabel('reaction-noise sigma'); axes[1].set_ylabel('Ndiv')
axes[1].set_title('Band robustness to additive noise (F=0.040,k=0.063)'); axes[1].grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUTDIR,'gs_band_fine.png'),dpi=130)
print("REPORT_DONE")
