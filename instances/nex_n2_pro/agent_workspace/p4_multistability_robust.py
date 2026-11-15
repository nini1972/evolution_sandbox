#!/usr/bin/env python3
"""
Lock down the multistability count at the P4 core:
 (A) SEED-COUNT PLATEAU: add seeds one by one at N=120; does N_distinct stop at 6
     or keep growing (tiny-basin attractors we haven't hit yet)?
 (B) N-SCALING: N in {48,96,192,384}; does the count of distinct period-4 attractors
     grow with N (spatially-localized family) or stay ~6 (small discrete set)?
Corrections from p4_12attractor_check: complement 1-S is NOT an attractor
(coupled(1-x)=coupled(x) => folding, not symmetry). Only high-branch S are attractors.
"""
import numpy as np, json, time
N_DEFAULT=120
def f(x,r): return r*x*(1.0-x)
def coupled(x,r,eps,N):
    fx=f(x,r); return (1.0-eps)*fx+(0.5*eps)*(np.roll(fx,1)+np.roll(fx,-1))
def lock(r,eps,trans,N,x0):
    x=x0.copy()
    for _ in range(trans): x=coupled(x,r,eps,N)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps,N)
    return P
def d_orbit(P,Q):
    N=P.shape[0]; best=np.inf
    Qr=[np.roll(Q,s,axis=0) for s in range(N)]
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for Qs in Qr:
            d=float(np.max(np.abs(Pt-Qs)))
            if d<best: best=d
    return best
def cluster_count(Ps,tol=1e-3):
    D=np.zeros((len(Ps),len(Ps)))
    for i in range(len(Ps)):
        for j in range(i,len(Ps)):
            D[i,j]=D[j,i]=d_orbit(Ps[i],Ps[j])
    rep=[]
    for i in range(len(Ps)):
        if all(D[i,ri]>tol for ri in rep): rep.append(i)
    return len(rep),D

r,eps=3.87,0.136
# ---------- (A) seed-count plateau at N=120 ----------
N=120; nseeds=48; trans=40000
rng=np.random.default_rng(7)
x0s=[rng.random(N) for _ in range(nseeds)]
t0=time.time()
Ps=[lock(r,eps,trans,N,x0s[i]) for i in range(nseeds)]
print(f"[A] extracted {nseeds} 4-tuples in {time.time()-t0:.1f}s; computing plateau...")
plateau=[]
# incremental: recompute count on prefixes by full re-cluster (cheap enough for 48)
for m in range(6,nseeds+1,3):
    c,_=cluster_count(Ps[:m])
    plateau.append((m,c))
    print(f"   seeds={m:2d}  N_distinct={c}")
# dominant wavenumbers of the final reps
cD,_=cluster_count(Ps)
rep,_=cluster_count(Ps)
print(f"[A] FINAL N=120, {nseeds} seeds -> N_distinct = {cD}")

# ---------- (B) N-scaling ----------
print("\n[B] N-scaling (10 seeds each, trans=25000):")
nsc={}
for Nn in [48,96,192,384]:
    tt0=time.time()
    rgg=np.random.default_rng(11)
    PsN=[lock(r,eps,25000,Nn,rgg.random(Nn)) for _ in range(10)]
    c,_=cluster_count(PsN)
    nsc[Nn]=c
    print(f"   N={Nn:3d}  N_distinct={c}  ({time.time()-tt0:.1f}s)")

# dominant wavenumber of each N=120 attractor (for the record)
def kdom(P):
    prof=np.mean(P,axis=1); F=np.abs(np.fft.rfft(prof-np.mean(prof)))
    k=np.argsort(F)[::-1][:2]+1
    return [int(x) for x in k]
cD,Dm=cluster_count(Ps)
reps_idx,_=cluster_count(Ps)
print("\n[A] dominant wavenumbers of the 6 N=120 attractors:")
for ri in reps_idx:
    print(f"   attr(rep idx {ri}): kdom={kdom(Ps[ri])}  mean={np.mean(Ps[ri]):.3f}")

json.dump({'r':r,'eps':eps,
           'A_seedcount_plateau':plateau,'A_final_N120_distinct':cD,
           'B_N_scaling':nsc,
           'N120_kdom':[kdom(Ps[ri]) for ri in reps_idx],
           'note':'complement 1-S is NOT an attractor (folding). count = high-branch period-4 attractors'},
          open('p4_multistability_robust.json','w'),indent=2)
print("\nsaved p4_multistability_robust.json")
