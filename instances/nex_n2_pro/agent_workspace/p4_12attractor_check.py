#!/usr/bin/env python3
"""
Verify the 12-attractor structure at the P4 core:
  high branch S  = 6 attractors (mean ~0.67)
  low branch 1-S = 6 complement attractors (mean ~0.33)
Confirm 1-S are genuine attractors (invariant under iteration), mutually distinct,
distinct from S, and count how many random seeds reach each of the 12 basins.
"""
import numpy as np, json
N=120
def f(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    fx=f(x,r); return (1.0-eps)*fx+(0.5*eps)*(np.roll(fx,1)+np.roll(fx,-1))
def lock(r,eps,trans,x0):
    x=x0.copy()
    for _ in range(trans): x=coupled(x,r,eps)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps)
    return P
def d_orbit(P,Q,comp=False):
    if comp: Q=1.0-Q
    best=np.inf
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for s in range(0,N,1):
            d=float(np.max(np.abs(Pt-np.roll(Q,s,axis=0))))
            if d<best: best=d
    return best
def is_attractor(P,r,eps,iters=2000,tol=1e-9):
    # iterate one snapshot 2000 steps; check it returns to the same 4-tuple (orbit closure)
    x=P[:,0].copy()
    for _ in range(iters): x=coupled(x,r,eps)
    # after iters steps, phase = iters mod 4
    P2=np.empty((N,4))
    for k in range(4): P2[:,k]=x; x=coupled(x,r,eps)
    return d_orbit(P,P2)  # small => 1-P / P is truly on the attractor

r,eps=3.87,0.136
hi=[lock(r,eps,40000,np.random.default_rng(s).random(N)) for s in range(6)]
lo=[1.0-p for p in hi]
print("== verify low-branch (complement) are genuine attractors ==")
for i,(p,pl) in enumerate(zip(hi,lo)):
    print(f"  hi{i}: closure={is_attractor(p,r,eps):.2e}  mean={np.mean(p):.3f}")
    print(f"  lo{i}(=1-hi{i}): closure={is_attractor(pl,r,eps):.2e}  mean={np.mean(pl):.3f}")

# full 12 x 12 d_orbit (no extra complement toggle; lo already = complement)
allp=hi+lo
M=np.zeros((12,12))
for i in range(12):
    for j in range(12): M[i,j]=d_orbit(allp[i],allp[j])
# cluster
rep=[];asg=[]
for i in range(12):
    pl=False
    for ri,R0 in enumerate(rep):
        if M[i,rep[ri]]<1e-3: asg.append(ri);pl=True;break
    if not pl: rep.append(i);asg.append(len(rep)-1)
print(f"\n12-candidate clustering -> N_distinct = {len(rep)}  (expect 12)")
print("branch of each:", ["hi" if i<6 else "lo" for i in rep])
# complement pairing hi<->lo
print("complement-pair check hi[i] vs lo[j] (small d = twin):")
for i in range(6):
    for j in range(6):
        d=d_orbit(allp[i],allp[6+j])
        if d<1e-3: print(f"  hi{i} <-> lo{j}  d={d:.1e}")

# basin count: 30 random seeds -> which of the 12 do they reach?
rng=np.random.default_rng(42)
cnt=np.zeros(12,int)
for t in range(30):
    P=lock(r,eps,20000,rng.random(N))
    best_j=0;best_d=np.inf
    for j in range(12):
        d=d_orbit(P,allp[j])
        if d<best_d: best_d=d;best_j=j
    cnt[best_j]+=1
print("\nbasin occupancy (30 seeds):", dict(zip(range(12),cnt.tolist())))
print("branches: hi=",int(cnt[:6].sum())," lo=",int(cnt[6:].sum()))
json.dump({'r':r,'eps':eps,'N_distinct_12':len(rep),'basin_30seeds':cnt.tolist(),
           'means_hi':[float(np.mean(p)) for p in hi],
           'means_lo':[float(np.mean(p)) for p in lo]},
          open('p4_12attractor_check.json','w'),indent=2)
print("\nsaved p4_12attractor_check.json")
