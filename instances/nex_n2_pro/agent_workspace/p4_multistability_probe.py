#!/usr/bin/env python3
"""
MULTISTABILITY PROBE for the P4 tongue (the f64-vs-ld diff of O(0.5) demands it).

If the P4 cell is a UNIQUE stable attractor, then:
  - all seeds -> identical locked 4-tuple (pairwise max-dist ~ 0)
  - f64 and longdouble (same x0) -> identical (diff ~ 1e-15)
If it is a MANIFOLD of coexisting P4 orbits (multistable), then:
  - seeds -> cluster into >=2 distinct locked 4-tuples
  - f64 vs ld (same x0, diff by O(1e-16)) -> different basins -> O(0.5)

We test cell (r=3.87, eps=0.136) [robust interior P4] and
          (r=3.865, eps=0.132) [edge / marginal].
"""
import json
import numpy as np

N = 120
def g(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    f=g(x,r)
    return (1.0-eps)*f + (0.5*eps)*(np.roll(f,1)+np.roll(f,-1))

def lock(r,eps,trans,seed,dtype=np.float64):
    x = np.random.default_rng(seed).random(N).astype(dtype)
    for _ in range(trans):
        x = coupled(x,r,eps).astype(dtype)
    P=np.empty((N,4),dtype=dtype)
    for k in range(4):
        P[:,k]=x; x=coupled(x,r,eps).astype(dtype)
    return P

def spread_of(P):
    # P4 amplitude of this orbit (max over sites & phases)
    return float(np.max(np.abs(P-P[:,0:1])))

def probe(r,eps,trans,seeds=(0,1,2,3,4,5),label=""):
    print(f"\n===== {label} cell r={r} eps={eps}  (N={N}) =====")
    P64=[lock(r,eps,trans,s,np.float64) for s in seeds]
    # pairwise max distances
    n=len(P64); D=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            D[i,j]=float(np.max(np.abs(P64[i]-P64[j])))
    # cluster: how many distinct orbits? (threshold 1e-3)
    rep=[]
    for i in range(n):
        if not any(float(np.max(np.abs(P64[i]-r0)))<1e-3 for r0 in rep):
            rep.append(P64[i])
    print(f"  n_seeds={n}  max pairwise dist={D.max():.3e}  n_distinct_orbits(>1e-3)={len(rep)}")
    for k,P in enumerate(P64):
        print(f"    seed{k}: spread={spread_of(P):.4f}  cell0={np.array2string(P[0],precision=4)}")
    # f64 vs longdouble, SAME seed 0
    a=lock(r,eps,trans,0,np.float64); b=lock(r,eps,trans,0,np.longdouble)
    d=float(np.max(np.abs(b.astype(np.float64)-a)))
    print(f"  f64 vs longdouble (same x0): max|diff|={d:.3e}")
    print(f"    f64 cell0 ={np.array2string(a[0],precision=5)}")
    print(f"    ld  cell0 ={np.array2string(b[0].astype(np.float64),precision=5)}")
    # perturbation response: seed0 locked + 1e-3 noise -> returns to same orbit or jumps?
    x0=lock(r,eps,trans,0,np.float64)[:,0]  # take phase-0 profile as IC
    x=x0+1e-3*(np.random.default_rng(7).random(N)-0.5)
    for _ in range(trans): x=coupled(x,r,eps)
    Pp=np.empty((N,4)); 
    for k in range(4): Pp[:,k]=x; x=coupled(x,r,eps)
    # min over 4-phase shift vs seed0 orbit
    dm=min(float(np.max(np.abs(Pp-np.roll(P64[0],sh,axis=1)))) for sh in range(4))
    print(f"  +1e-3 perturbation: min-over-phase dist to seed0 orbit = {dm:.3e}")
    print(f"    -> {'SAME orbit (isolated attractor)' if dm<1e-3 else 'JUMPED to another P4 (multistable manifold)'}")
    return dict(r=r,eps=eps,n_distinct=len(rep),max_pairwise=float(D.max()),
                f64_ld_diff=d, perturbation_dist=dm,
                orbits_distinct=dm>1e-3)

res=[probe(3.87,0.136,trans=10000,label="CORE (interior, robust P4)"),
     probe(3.865,0.132,trans=10000,label="EDGE (marginal, near-lock)")]
with open('p4_multistability_probe.json','w') as f: json.dump(res,f,indent=2)
print("\nsaved p4_multistability_probe.json")
