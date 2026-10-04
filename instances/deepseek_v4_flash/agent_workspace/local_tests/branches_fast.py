"""
Streamlined branch scan + nucleation test.
Branches via vectorized grid; nucleation with one representative (a=2, K0=6).
"""
import numpy as np
from scipy.integrate import quad

def g(w): return 1.0/(np.pi*(1.0+w*w))
def I(B):
    if B <= 0: return 0.0
    return quad(lambda w: g(w)*np.sqrt(max(0.0,1-(w/B)**2)), -B, B, limit=200)[0]

def branches(a, K0, grid=None):
    h = lambda R: R - I(K0*R**a)
    if grid is None: grid = np.linspace(1e-3, 0.999, 600)
    vals = np.array([h(R) for R in grid])
    out = []
    for i in range(1, len(grid)):
        if vals[i-1] < 0 <= vals[i] or vals[i-1] > 0 >= vals[i]:
            lo, hi = grid[i-1], grid[i]
            for _ in range(40):
                mid = 0.5*(lo+hi)
                if h(mid) < 0: lo = mid
                else: hi = mid
            out.append(0.5*(lo+hi))
    return out

def simulate_R(a, K0, N=4000, T=120.0, dt=0.02, seed=11, seedR0=None):
    r = np.random.default_rng(seed)
    om = np.tan(np.pi*(r.random(N)-0.5))
    th = r.uniform(0, 2*np.pi, N)
    if seedR0:
        n0 = int(N*seedR0); psi0 = 0.3
        th[:n0] = psi0 + 0.05*r.standard_normal(n0)
    steps = int(T/dt); nw = max(1, int(0.2*steps)); buf = []
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        th = (th + om*dt + K0*(R**a)*np.sin(psi-th)*dt) % (2*np.pi)
        buf.append(R)
        if len(buf) > nw: buf.pop(0)
    return float(np.mean(buf))

print("Branches R* = I(K0^a R) | roots of R - I(K0 R^a) = 0:")
for a in [0.0, 0.5, 1.0, 2.0]:
    for K0 in [3.0, 6.0]:
        print(f"  a={a:3.1f} K0={K0:4.1f}: {[f'{b:.4f}' for b in branches(a,K0)]}")
print("\nOnset scan (supercritical a<=1: R(seed~0) should jump near K0=2):")
for a in [0.0, 0.5, 1.0]:
    for K0 in [1.5, 2.0, 2.5, 3.0]:
        print(f"  a={a:3.1f} K0={K0:4.1f}: R_ss={simulate_R(a,K0,seedR0=0.02):.4f}")
print("\nNucleation (a=2, subcritical):")
for K0 in [5.0, 6.0]:
    for R0 in [0.03, 0.5]:
        print(f"  K0={K0:4.1f} seedR0={R0}: R_ss={simulate_R(2.0,K0,seedR0=R0):.4f}")