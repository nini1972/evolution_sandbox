#!/usr/bin/env python3
"""
STRUCTURE OF THE 6 COEXISTING P4 ATTRACTORS at the tongue core.
Symmetries of the logistic CML x_i -> (1-eps)f(x_i)+(eps/2)(f(x_{i-1})+f(x_{i+1})):
  S1 time phase (roll 4)          [factored by d_orbit]
  S2 spatial site shift (ring)    [factored by d_orbit]
  S3 global complement x -> 1-x   [f(1-x)=f(x) => NOT factored; tested here]
Question: do the 6 collapse to 3 under S3?  And what are their k-modes / traveling-vs-standing?
"""
import numpy as np, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N=120
def f(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    fx=f(x,r); return (1.0-eps)*fx+(0.5*eps)*(np.roll(fx,1)+np.roll(fx,-1))
def lock(r,eps,trans,seed):
    x=np.random.default_rng(seed).random(N)
    for _ in range(trans): x=coupled(x,r,eps)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps)
    return P

def minmax_shift(A,B):
    # A,B (N,). min over site shift s of max|A - roll(B,s)|
    best=np.inf
    for s in range(0,N,1):
        d=float(np.max(np.abs(A-np.roll(B,s))))
        if d<best: best=d
    return best

def d_orbit_full(P,Q,comp=False):
    # P,Q (N,4); min over time-phase p and site shift s of max|Pt - roll(Q,s)|
    if comp: Q=1.0-Q
    best=np.inf
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for s in range(0,N,1):
            Qs=np.roll(Q,s,axis=0)
            d=float(np.max(np.abs(Pt-Qs)))
            if d<best: best=d
    return best

def spectrum(profile):
    F=np.fft.rfft(profile-np.mean(profile))
    return np.abs(F)

r,eps=3.87,0.136
seeds=list(range(6))
Ps=[lock(r,eps,40000,s) for s in seeds]
print(f"core r={r} eps={eps}: {len(Ps)} attractors extracted\n")

# --- complement pairing: d_orbit_full(P_i, P_j, comp=True) ---
print("Complement-twin test:  d_orbit(P_i, 1-P_j)  [small => i and j are complement twins]")
Cm=np.zeros((6,6))
for i in range(6):
    for j in range(6):
        Cm[i,j]=d_orbit_full(Ps[i],Ps[j],comp=True)
print("   "+" ".join(f"  j{j}" for j in range(6)))
for i in range(6):
    print(f"i{i} "+" ".join(f"{Cm[i,j]:6.2e}" for j in range(6)))
# group into complement pairs
twin=[None]*6
for i in range(6):
    for j in range(i+1,6):
        if Cm[i,j]<1e-3 and twin[i] is None and twin[j] is None:
            twin[i]=j; twin[j]=i
print("twin pairs (i<->j via x->1-x):", [(i,twin[i]) for i in range(6) if twin[i] is not None and i<twin[i]])
n_fam=len([i for i in range(6) if twin[i] is None or i<twin[i]])
print(f"=> distinct pattern families (mod time, site, complement) = {n_fam}\n")

# --- per-attractor spatial structure ---
info={}
for i,P in enumerate(Ps):
    prof=np.mean(P,axis=1)          # mean over 4 time snapshots
    amp=(np.max(P)-np.min(P))/2.0   # oscillation amplitude per site (max over site&time)
    spec=spectrum(prof)
    # dominant nonzero wavenumbers (exclude k=0 mean)
    kdom=np.argsort(spec)[::-1][:3]+1  # rfft index 1..N/2 = wavenumber
    info[i]={'mean':float(np.mean(prof)),'amp':float(amp),'kdom':[int(k) for k in kdom],
             'spec_top':[float(spec[k-1]) for k in kdom]}
    print(f"attr {i}: mean={np.mean(prof):.3f}  amp={amp:.3f}  top-k(wave)={[int(k) for k in kdom]}  spec={[f'{float(spec[k-1]):.1f}' for k in kdom]}")

# --- traveling vs standing: does the pattern rotate? ---
print("\nTraveling-wave test (does site profile at t=k relate by a fixed spatial shift?):")
for i,P in enumerate(Ps):
    # estimate shift between snapshot 0 and snapshot 1
    A=P[:,0]; best_s=0;best_d=np.inf
    for s in range(0,N):
        d=float(np.max(np.abs(A-np.roll(P[:,1],s))))
        if d<best_d: best_d=d;best_s=s
    # and between 0 and 2 (should be 2x)
    A0=P[:,0]; best_s2=0;best_d2=np.inf
    for s in range(0,N):
        d=float(np.max(np.abs(A0-np.roll(P[:,2],s))))
        if d<best_d2: best_d2=d;best_s2=s
    print(f"attr {i}: shift(t0->t1)={best_s:3d} (d={best_d:.2e})   shift(t0->t2)={best_s2:3d} (d={best_d2:.2e})   "
          f"=> {'traveling (rotates)' if best_d<1e-2 and best_d2<1e-2 else ('standing/symmetric' if best_d<1e-2 else 'mixed')}")

json.dump({'r':r,'eps':eps,'n_extracted':6,'n_families_mod_complement':n_fam,
           'twin_pairs':[[i,twin[i]] for i in range(6) if twin[i] is not None and i<twin[i]],
           'per_attractor':info}, open('p4_attractor_structure.json','w'), indent=2)

# --- PLOT ---
fig,axes=plt.subplots(2,3,figsize=(16,7),sharex=True)
for i,(ax,P) in enumerate(zip(axes.ravel(),Ps)):
    prof=np.mean(P,axis=1)
    ax.plot(prof,lw=1.4)
    ax.set_title(f"attr {i} (mean over 4 phases)  kdom={[int(k) for k in (np.argsort(spectrum(prof))[::-1][:2]+1)]}",fontsize=10)
    ax.set_xlabel("site"); ax.set_ylabel("x")
    ax.grid(alpha=.3)
fig.suptitle(f"P4 tongue core r={r}, eps={eps}: 6 coexisting attractors (complement-twin pairs tested)")
plt.tight_layout()
plt.savefig('p4_attractor_structure.png',dpi=110)
print("\nsaved p4_attractor_structure.png, p4_attractor_structure.json")
