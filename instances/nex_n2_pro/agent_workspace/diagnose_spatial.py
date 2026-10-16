#!/usr/bin/env python3
"""What IS the P4 spatial structure? Candidates:
 (A) checkerboard x_i = c_{i mod 2}                (2-value, static)
 (B) spatial period-4 static x_i = c_{i mod 4}
 (C) traveling wave  x_i(t) = c_{(i+t) mod 4}
 (D) traveling wave with k-site shift per step: x_i(t) = c_{(i + k t) mod p}
 (E) other (measured profile)
"""
import numpy as np

def coupled(x, r, eps):
    f = r*x*(1.0-x)
    return (1.0-eps)*f + (eps/2.0)*(np.roll(f,1)+np.roll(f,-1))

r, eps, N = 3.865, 0.135, 120
np.random.seed(0)
x = np.random.rand(N)
for _ in range(15000): x = coupled(x, r, eps)

frames = []
for t in range(8):
    frames.append(x.copy())
    x = coupled(x, r, eps)

X = np.array(frames)  # (8, N)
print("t=0 first 16 sites:\n", np.round(X[0][:16], 4))
print("t=1 first 16 sites:\n", np.round(X[1][:16], 4))

# (B) static period-4 in space at fixed t
for t in range(4):
    c = np.array([X[t][k::4].mean() for k in range(4)])
    dev = max(abs(X[t][k] - c[k % 4]) for k in range(N))
    print("t=%d static-p4 profile c=%s  maxdev=%.4e" % (t, np.round(c,4), dev))

# (C) traveling wave x_i(t) = c_{(i+t) mod 4}
for t in range(4):
    c = np.array([X[t][(k - t) % 4::4].mean() for k in range(4)])
    dev = max(abs(X[t][i] - c[(i + t) % 4]) for i in range(N))
    print("t=%d wave-(i+t)mod4 profile c=%s  maxdev=%.4e" % (t, np.round(c,4), dev))

# (D) general shift: correlation X[t] with roll(X[t+1], -k) for all k
print("\nshift detection: corr(X[t], roll(X[t+1],-k)) for t=0..3, top shifts:")
for t in range(3):
    cors = []
    for k in range(N):
        cors.append((np.corrcoef(X[t], np.roll(X[t+1], -k))[0,1], k))
    cors.sort(reverse=True)
    print("  t=%d -> t+1 : best k=%d corr=%.4f  (k=0 corr=%.4f)" % (
        t, cors[0][1], cors[0][0], np.corrcoef(X[t], X[t+1])[0,1]))

# check P4 in time strictly
s4 = np.max(np.abs(X[4:] - X[:4]), axis=0)
print("\nperiod-4 in time: max|x(t)-x(t+4)| = %.3e across all N" % s4.max())
# and the 4 distinct phases:
print("phase0 first 12:", np.round(X[0][:12],3))
print("phase1 first 12:", np.round(X[1][:12],3))
print("phase2 first 12:", np.round(X[2][:12],3))
print("phase3 first 12:", np.round(X[3][:12],3))
np.save("p4_frames.npy", X)
