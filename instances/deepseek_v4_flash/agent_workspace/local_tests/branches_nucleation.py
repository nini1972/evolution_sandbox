"""
FIXED branch analysis for R = I(K0 R^a):
  * a<1: single stable branch, onset from R=0 at K0 = 1/I'(0) = 2
  * a=1: classic, R=sqrt(1-2/K0), onset K0=2
  * a>1: subcritical onset at K0*=2a/(a-1); nucleation seed needed above it
Test a=2, K0=6: theory says K0>K0*=4 -> sync branch exists but R=0 is locally stable.
Sim: seed with small bias vs large bias (R0=0.6) — expect small stays ~0, large -> ~0.5.
Also validate a=0.5 branch (supercritical from K0=2).
"""
import numpy as np
from scipy.integrate import quad

def g(w): return 1.0/(np.pi*(1.0+w*w))
def I(B):
    if B <= 0: return 0.0
    return quad(lambda w: g(w)*np.sqrt(max(0.0,1-(w/B)**2)), -B, B, limit=200)[0]

def branches(a, K0):
    """Return all stable branch values R* in (0,1]: scan roots of R - I(K0 R^a)."""
    def h(R): return R - I(K0*R**a)
    out = []
    # scan fine grid, bracket sign changes away from R=0
    grid = np.linspace(1e-4, 0.9999, 4000)
    prev = (0.0, h(1e-4))
    for R in grid:
        val = h(R)
        if prev[1] < 0 <= val or prev[1] > 0 >= val:
            # bisect
            lo, hi = prev[0], R
            for _ in range(60):
                mid = 0.5*(lo+hi)
                if h(mid) < 0: lo = mid
                else: hi = mid
            out.append(0.5*(lo+hi))
        prev = (R, val)
    return out

def simulate_R(a, K0, N=8000, T=400.0, dt=0.02, seed=11, seedR0=None):
    r = np.random.default_rng(seed)
    om = np.tan(np.pi*(r.random(N)-0.5))
    th = r.uniform(0, 2*np.pi, N)
    if seedR0 is not None:
        # create initial cluster of size seedR0 with phases psi0
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

print("Branch structure R* = I(K0 R^a):")
for a in [0.0, 0.5, 1.0, 2.0]:
    for K0 in [3.0, 4.0, 6.0]:
        br = branches(a, K0)
        print(f"  a={a:3.1f} K0={K0:4.1f}: stable branches {[f'{b:.4f}' for b in br]}")
print("\nNucleation test a=2:")
for K0 in [4.0, 6.0]:
    for R0 in [None, 0.05, 0.4, 0.7]:
        Rs = simulate_R(2.0, K0, seedR0=R0)
        print(f"  K0={K0:4.1f} seedR0={str(R0):>6}: R_ss={Rs:.4f}")
print("\nSupercritical onset check a=0.5 (theory: onset K0=2):")
for K0 in [1.5, 2.5, 3.0]:
    print(f"  K0={K0:4.1f}: R_ss(seed~0)={simulate_R(0.5, K0, seedR0=0.02):.4f}")