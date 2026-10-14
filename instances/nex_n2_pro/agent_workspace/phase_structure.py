#!/usr/bin/env python3
"""PHASE STRUCTURE + LOCK-WINDOW of the eps-induced P4 state at r=3.865.

Q1. Machine-precision test (decisive_test.py) proved: at r=3.865, eps=0.132
    ALL 120 cells sit on EXACT period-4 orbits (s4=0 to 16 decimals), with a
    tiny but real A-C split (~2e-4) — i.e. a genuine 4-cycle, NOT period-2
    and NOT banded chaos. But a UNIFORM lattice state (all cells equal) is
    impossible: it would reduce to the uncoupled map, which is chaotic at
    r=3.865. So the lock MUST be non-uniform. How is the space organized?
    -> Cluster the 120 4-tuples; inspect spatial arrangement + phase relations.

Q2. Map the lock window in eps at r=3.865 (exact s4 criterion):
    fraction locked-P4, locked-P2, aperiodic; median A-C split vs eps.
"""
import numpy as np
from collections import Counter

def coupled(x, r, eps):
    f = r*x*(1.0 - x)
    return (1.0 - eps)*f + (eps/2.0)*(np.roll(f,1) + np.roll(f,-1))

def run(n, r, eps, trans, rec):
    x = np.random.rand(n)
    for _ in range(trans):
        x = coupled(x, r, eps)
    S = np.empty((rec, n))
    for t in range(rec):
        x = coupled(x, r, eps); S[t] = x
    return S

def s_k(ts, k):
    return float(np.max(np.abs(ts[k:] - ts[:-k])))

def period_of(ts):
    # smallest k in set with exact repetition, else None
    for k in (1, 2, 3, 4, 6, 8, 12, 16):
        if s_k(ts, k) < 1e-9:
            return k
    return None

# ---------------- Q1: spatial organization at the locked point ----------------
print("=== Q1: spatial organization at r=3.865, eps=0.132 (120-cell ring) ===")
n, r, eps = 120, 3.865, 0.132
S = run(n, r, eps, trans=10000, rec=400)
tups = S[-4:].T  # shape (n,4): each cell's 4-tuple
# cluster 4-tuples by identity (tolerance 1e-6)
clusters = []
assign = np.full(n, -1)
for i in range(n):
    found = -1
    for ci, rep in enumerate(clusters):
        if np.max(np.abs(tups[i] - rep)) < 1e-6:
            found = ci; break
    if found < 0:
        clusters.append(tups[i]); found = len(clusters) - 1
    assign[i] = found

cnt = Counter(assign.tolist())
print("  distinct 4-tuples (clusters):", len(clusters))
for ci in range(len(clusters)):
    members = [i for i in range(n) if assign[i] == ci]
    print("  cluster %d : %d cells, members=%s" % (ci, len(members), members[:14]))
    v = tups[members[0]]
    print("    4-tuple = " + " ".join("%.8f" % a for a in v))
    print("    A-C=%.2e B-D=%.2e" % (v[0]-v[2], v[1]-v[3]))
# phase relation: is any cluster a cyclic rotation of another?
print("  rotation relations between clusters:")
for a in range(len(clusters)):
    for b in range(a+1, len(clusters)):
        A = clusters[a]
        for p in range(1, 4):
            if np.max(np.abs(np.roll(A, p) - clusters[b])) < 1e-6:
                print("    cluster %d = rotation(+%d) of cluster %d" % (b, p, a))
# spatial adjacency: how many neighboring pairs share a cluster?
same_adj = sum(1 for i in range(n) if assign[i] == assign[(i+1) % n])
print("  ring edges with same-cluster endpoints: %d / %d" % (same_adj, n))

# ---------------- Q2: lock window in eps ----------------
print()
print("=== Q2: lock window in eps at r=3.865 (exact s4 criterion) ===")
print("   eps   P4/120  P2/120  aperi/120  median|A-C|")
for e in [0.05, 0.08, 0.10, 0.11, 0.12, 0.13, 0.132, 0.14, 0.15,
          0.16, 0.18, 0.20, 0.25, 0.30]:
    S = run(n, r, e, trans=10000, rec=400)
    n4 = n2 = na = 0
    splits = []
    for i in range(n):
        p = period_of(S[:, i])
        if p == 4:
            n4 += 1
            splits.append(abs(S[-1, i] - S[-3, i]))  # |A - C|
        elif p == 2:
            n2 += 1
        else:
            na += 1
    med = float(np.median(splits)) if splits else float("nan")
    print("  %-6g  %3d/120  %3d/120   %3d/120    %.3e" % (e, n4, n2, na, med))
