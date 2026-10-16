#!/usr/bin/env python3
"""Decisive test: are the P4-classified lattices truly P4, or P2 checkerboards
with slowly-relaxing P4 domain defects?

Measure after T-trans iterations (increasing T):
  - bulk-only (sites 15..104): is it P2? P4?
  - ring-only  (sites 0..14):  is it P2? P4?
  - bulk amplitude of the checkerboard oscillation in time
"""
import numpy as np

def coupled(x, r, eps):
    f = r*x*(1.0-x)
    return (1.0-eps)*f + (eps/2.0)*(np.roll(f,1)+np.roll(f,-1))

r, eps, N = 3.865, 0.135, 120

def classify(S, tol=1e-9):
    """S: (T>=4, n) frames. returns (frac_P2, frac_P4, frac_P8plus) over sites."""
    s2 = np.max(np.abs(S[2:,:]-S[:-2,:]),axis=0)
    s4 = np.max(np.abs(S[4:,:]-S[:-4,:]),axis=0)
    s8 = np.max(np.abs(S[8:,:]-S[:-8,:]),axis=0) if S.shape[0]>=9 else np.ones(S.shape[1])
    p2 = int(np.sum(s2<tol)); p4 = int(np.sum((s2>=tol)&(s4<tol)))
    p8 = int(np.sum((s4>=tol)&(s8<tol))); pa = int(np.sum(s8>=tol))
    return p2,p4,p8,pa

for Ttrans in (15000, 50000, 200000):
    np.random.seed(0)
    x = np.random.rand(N)
    for _ in range(Ttrans):
        x = coupled(x, r, eps)
    S = np.empty((48,N))
    for t in range(48):
        x = coupled(x,r,eps); S[t]=x
    b = (classify(S[:,15:105])[1], classify(S[:,15:105])[0], classify(S[:,15:105])[2:4])
    r_ = classify(S[:,:15])
    p2b, p4b, (p8b, pab) = b
    print("Ttrans=%7d | BULK(89): P2=%d P4=%d P8+=%d | RING(15): P2=%d P4=%d P8+=%d"
          % (Ttrans, p2b, p4b, p8b+pab, r_[0], r_[1], r_[2]+r_[3]))
    # bulk oscillation amplitudes
    even = S[:,15::2][:, :44]  # just sample
    e0 = S[0, 15::2]; e2 = S[2, 15::2]; e4 = S[4, 15::2]
    print("   bulk even sites: max|e(t)-e(t+2)| = %.3e   max|e(t)-e(t+4)| = %.3e"
          % (np.max(np.abs(e0-e2)), np.max(np.abs(e0-e4))))
    print("   bulk even value range over t=0..47: %.6f .. %.6f (spread %.2e)"
          % (np.min(S[:,15::2]), np.max(S[:,15::2]),
             np.max(S[:,15::2])-np.min(S[:,15::2])))
    print("   even site15 orbit t=0..7:", np.round(S[:8,15],6))
    print("   ring site3  orbit t=0..7:", np.round(S[:8,3],6))
