"""
UNIVERSAL STATIONARY LAW for the family  dθ/dt = ω + K0 * R^a * sin(ψ-θ):
      R_ss = I(K0 * R_ss^a),   I(B) = ∫_{|w|<B} g(w) sqrt(1-(w/B)^2) dw
  * a=1 -> classic Kuramoto: R = sqrt(1 - 2g/K0)  (K0>2)
  * a=0 -> fixed-field model: R = I(K0)
  * a=0.5, 2 -> interpolated predictions to be verified by simulation
Test across a in {0,0.5,1,2}, K0 in {3, 6}: compare sim vs I(K0 R^a).
"""
import numpy as np
from scipy.integrate import quad

def g(w): return 1.0/(np.pi*(1.0+w*w))
def I(B):
    if B <= 0: return 0.0
    return quad(lambda w: g(w)*np.sqrt(max(0.0,1-(w/B)**2)), -B, B, limit=200)[0]

def R_theory(a, K0):
    # solve R = I(K0 R^a) by bisection on [0,1]
    def h(R): return R - I(K0*R**a)
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if h(mid) > 0: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def simulate(a, K0, N=4000, T=300.0, dt=0.02, seed=11):
    r = np.random.default_rng(seed)
    om = np.tan(np.pi*(r.random(N)-0.5))
    th = r.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        K = K0*(R**a)
        th = (th + om*dt + K*np.sin(psi-th)*dt) % (2*np.pi)
    # average over last 20% via returning running window
    return None

def simulate_R(a, K0, N=4000, T=300.0, dt=0.02, seed=11):
    r = np.random.default_rng(seed)
    om = np.tan(np.pi*(r.random(N)-0.5))
    th = r.uniform(0, 2*np.pi, N)
    steps = int(T/dt); nw = max(1, int(0.2*steps)); buf = []
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        th = (th + om*dt + K0*(R**a)*np.sin(psi-th)*dt) % (2*np.pi)
        buf.append(R)
        if len(buf) > nw: buf.pop(0)
    return float(np.mean(buf)), float(np.std(buf))

print(f"{'a':>4} {'K0':>4} {'theory R':>9} {'sim R':>8} {'sim sd':>8}  match")
for a in [0.0, 0.5, 1.0, 2.0]:
    for K0 in [3.0, 6.0]:
        Rt = R_theory(a, K0)
        Rs, sd = simulate_R(a, K0)
        ok = "OK " if abs(Rs-Rt) < 0.02 else "MISMATCH"
        print(f"{a:4.1f} {K0:4.1f} {Rt:9.4f} {Rs:8.4f} {sd:8.4f}  {ok}")
print("\nclassic a=1 anchors: sqrt(1-2/3)=0.5774, sqrt(1-2/6)=0.8165")
print("fixed-field a=0 anchors: I(3)=0.7208, I(6)=0.8471")