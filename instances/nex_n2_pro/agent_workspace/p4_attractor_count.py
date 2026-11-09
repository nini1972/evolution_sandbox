#!/usr/bin/env python3
"""
DECISIVE MULTIATTRACTOR COUNT for the P4 tongue, using the CORRECT orbit
invariant: two period-4 trajectories are the SAME attractor iff one 4-tuple can
be transformed into the other by (i) a time-phase roll (mod 4) AND (ii) a spatial
translation of the ring (mod N).  Without factoring out (i) and (ii) every
different phase / spatial origin looks like a new 'orbit'.

  d_orbit(P, Q) = min_{p in 0..3, s in 0..N-1} max|x| of
                  ( P[:, :, roll by p in time]  vs  roll(Q, s, axis=site) )
  P, Q : (N,4) arrays = 4 consecutive snapshots.

If all seeds collapse to ONE representative -> single attractor family
(mod Z_N spatial symmetry + time phase).  If they split into K clusters ->
K genuinely coexisting period-4 attractors (true multistability).
"""
import json
import numpy as np

N=120
def g(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    f=g(x,r); return (1.0-eps)*f+(0.5*eps)*(np.roll(f,1)+np.roll(f,-1))

def lock(r,eps,trans,seed):
    x=np.random.default_rng(seed).random(N)
    for _ in range(trans): x=coupled(x,r,eps)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps)
    return P

def d_orbit(P,Q):
    # P,Q: (N,4).  min over time-phase p (roll P along time axis) and spatial
    # shift s (roll Q along site axis).
    best=np.inf
    Ns=N
    Qr=[np.roll(Q,s,axis=0) for s in range(0,Ns,  # step by 1 is exact; keep 1
         1)]
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for Qs in Qr:
            d=float(np.max(np.abs(Pt-Qs)))
            if d<best: best=d
    return best

def count_attractors(r,eps,trans,seeds,tol=1e-3,label=""):
    Ps=[lock(r,eps,trans,s) for s in seeds]
    rep=[]
    assign=[]
    for i,P in enumerate(Ps):
        placed=False
        for ri,R0 in enumerate(rep):
            if d_orbit(P,R0)<tol:
                assign.append(ri); placed=True; break
        if not placed:
            rep.append(P); assign.append(len(rep)-1)
    print(f"\n=== {label}  r={r} eps={eps} trans={trans} ===")
    print(f"  n_seeds={len(seeds)}  ->  N_distinct_attractors(mod phase&site-shift) = {len(rep)}")
    # pairwise d_orbit matrix
    n=len(Ps); D=np.zeros((n,n))
    for i in range(n):
        for j in range(n): D[i,j]=d_orbit(Ps[i],Ps[j])
    print(f"  pairwise d_orbit (min over phase x site):")
    print("       "+" ".join(f"s{j:>2d}" for j in range(n)))
    for i in range(n):
        print(f"  s{i}  "+" ".join(f"{D[i,j]:.1e}" for j in range(n)))
    print(f"  cluster assignment: {assign}")
    return len(rep), assign, D

def f64_vs_ld(r,eps,trans,label=""):
    def lockd(dtype):
        x=np.random.default_rng(0).random(N).astype(dtype)
        for _ in range(trans): x=coupled(x,r,eps).astype(dtype)
        P=np.empty((N,4),dtype=dtype)
        for k in range(4): P[:,k]=x; x=coupled(x,r,eps).astype(dtype)
        return P
    a=lockd(np.float64); b=lockd(np.longdouble)
    d_raw=float(np.max(np.abs(b.astype(np.float64)-a)))
    d_inv=d_orbit(a,b.astype(np.float64))
    print(f"\n  [f64 vs longdouble] {label} r={r} eps={eps}: raw={d_raw:.3e}  d_orbit(mod phase&site)={d_inv:.3e}")
    print(f"    -> {'SAME attractor (phase/site shift)' if d_inv<1e-3 else 'DIFFERENT attractor (genuine f64/ld split)'}")
    return d_raw, d_inv

for (r,eps,lab) in [(3.87,0.136,"CORE"),(3.865,0.132,"EDGE")]:
    n,asg,D=count_attractors(r,eps,trans=40000,seeds=list(range(6)),label=lab)
    f64_vs_ld(r,eps,trans=40000,label=lab)

print("\n\n==== INTERPRETATION ====")
print("n_distinct=1  -> single P4 attractor family (isolated, mod ring symmetry): CLEAN.")
print("n_distinct>1  -> genuine multistability: K coexisting period-4 attractors;")
print("                 basin selection matters; surrogates/null-bracket must average or")
print("                 condition on the realized basin.")
