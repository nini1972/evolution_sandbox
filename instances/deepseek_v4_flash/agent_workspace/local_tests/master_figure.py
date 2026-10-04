"""
MASTER FIGURE (efficient version): precompute I(B) once on a grid, interpolate.
"""
import numpy as np
from scipy.integrate import quad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def g(w): return 1.0/(np.pi*(1.0+w*w))
# precompute I(B) table
Bgrid = np.linspace(0, 12, 2401)
Itab = np.array([quad(lambda w: g(w)*np.sqrt(max(0.0,1-(w/B)**2)), -B, B, limit=100)[0] if B > 1e-9 else 0.0 for B in Bgrid])
def I(B): return np.interp(B, Bgrid, Itab)

def branch_R(a, K0):
    h = lambda R: R - I(K0*R**a)
    grid = np.linspace(1e-3, 0.999, 400)
    vals = np.array([h(R) for R in grid])
    roots = []
    for i in range(1, len(grid)):
        if vals[i-1] < 0 <= vals[i] or vals[i-1] > 0 >= vals[i]:
            lo, hi = grid[i-1], grid[i]
            for _ in range(30):
                mid = 0.5*(lo+hi)
                if h(mid) < 0: lo = mid
                else: hi = mid
            roots.append(0.5*(lo+hi))
    return roots

def sim_R(a, K0, N=2500, T=60.0, dt=0.02, seed=11, seedR0=None):
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

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
colors = {0.0:'#1f77b4', 0.5:'#2ca02c', 1.0:'#d62728', 2.0:'#9467bd'}

# ---------- Panel 1: R*(K0) ----------
ax = axes[0,0]
Kgrid = np.linspace(0.1, 8, 180)
for a in [0.0, 0.5, 1.0, 2.0]:
    Rst = [max(branch_R(a,K0)) if branch_R(a,K0) else np.nan for K0 in Kgrid]
    ax.plot(Kgrid, Rst, color=colors[a], lw=2, label=f'a={a:g}')
for a, K0s in [(0.0,[2.0,3.0,6.0]),(0.5,[2.0,3.0,6.0]),(1.0,[2.0,2.5,3.0,6.0]),(2.0,[6.0])]:
    for K0 in K0s:
        Rs = sim_R(a, K0)
        ax.plot(K0, Rs, 'o', mfc=colors[a], mec='k', ms=8)
ax.axhline(0, color='k', lw=0.5); ax.axvline(2, color='gray', ls=':', lw=1)
ax.set_xlabel('K0'); ax.set_ylabel('R* (stationary order)')
ax.set_title('Universal law  R* = I(K0 R*^a)  (points = simulation)')
ax.legend(fontsize=8); ax.set_ylim(-0.02, 1.02)

# ---------- Panel 2: a=2 subcritical hysteresis ----------
ax = axes[0,1]
Ksn = 4.0
kvals = np.linspace(Ksn, 8, 150)
for K0 in kvals:
    roots = branch_R(2.0, K0)
    if len(roots) >= 2:
        ax.plot(K0, roots[0], '.', color='gray', ms=2)
        ax.plot(K0, roots[-1], '.', color=colors[2.0], ms=2)
    elif len(roots) == 1:
        ax.plot(K0, roots[0], '.', color=colors[2.0], ms=2)
for K0, R0, Rs in [(5.0,0.03,0.0165),(5.0,0.5,0.0130),(6.0,0.03,0.0166),(6.0,0.5,0.7508)]:
    ax.plot(K0, Rs, 's', mfc='red' if Rs<0.1 else 'green', mec='k', ms=10)
    ax.annotate(f'R0={R0:g}', (K0, Rs), textcoords='offset points', xytext=(6,6), fontsize=7)
ax.axvline(Ksn, color='k', ls='--', lw=1.2)
ax.text(Ksn+0.1, 0.5, 'saddle-node\nK0*=4', fontsize=9)
ax.set_xlabel('K0'); ax.set_ylabel('R*')
ax.set_title('a=2 subcritical: hysteresis (green=nucleated, red=decayed)')
ax.set_ylim(-0.02, 1.02); ax.set_xlim(2, 8)

# ---------- Panel 3: drift phasor ----------
ax = axes[1,0]
ss = np.linspace(1.05, 5.0, 50)
mx, my = [], []
for s in ss:
    a_ = np.linspace(0, 2*np.pi, 2000)
    den = s - np.sin(a_)
    mx.append(np.trapezoid(np.cos(a_)/den, a_)/np.trapezoid(1.0/den, a_))
    my.append(np.trapezoid(np.sin(a_)/den, a_)/np.trapezoid(1.0/den, a_))
ax.plot(ss, mx, 'o-', ms=2, label='<cos> (aligned) = 0', color='#1f77b4')
ax.plot(ss, my, 's-', ms=2, label='<sin> (perpendicular)', color='#d62728')
ax.plot(ss, ss - np.sqrt(ss**2 - 1), 'k--', lw=1, label='analytic s-√(s²-1)')
ax.set_xlabel('s = |ω|/K_eff'); ax.set_ylabel('drift mean phasor components')
ax.set_title('Drifting oscillators: mean phasor is PERPENDICULAR')
ax.legend(fontsize=8)

# ---------- Panel 4: a=1 OA kinetics ----------
ax = axes[1,1]
from scipy.integrate import solve_ivp
K0 = 3.0
def RHS(t, y): return (K0/2.0)*y[0]*(1 - y[0]**2) - y[0]
tgrid = np.linspace(0, 10, 400)
for R0 in [0.01, 0.3, 0.7]:
    sol = solve_ivp(RHS, [0,10], [R0], t_eval=tgrid, rtol=1e-9)
    ax.plot(sol.t, sol.y[0], lw=1.5, label=f'OA kinetics R0={R0:g}')
ax.axhline(np.sqrt(1-2/K0), color='k', ls='--', lw=1)
ax.text(1, 0.62, '√(1-2/K₀)=0.577', fontsize=8)
ax.set_xlabel('t'); ax.set_ylabel('R(t)')
ax.set_title('a=1 = classic Kuramoto: OA kinetics (K0=3)')
ax.legend(fontsize=8)

plt.tight_layout()
fig.savefig('../outputs/reflexive_kuramoto_phase_diagram.png', dpi=140, bbox_inches='tight')
print("saved ../outputs/reflexive_kuramoto_phase_diagram.png")

import json
data = {
 "universal_law": "R* = I(K0 R*^a), I(B)=int_{|w|<B} g(w) sqrt(1-(w/B)^2) dw",
 "a1_classic": {"Kc": 2.0, "R": "sqrt(1-2/K0)", "K0_3": 0.5774, "sim_3": None, "K0_6": 0.8165},
 "a0_fixedfield": {"R": "I(K0)", "K0_3": 0.7208, "K0_6": 0.8471},
 "a2_subcritical": {"Ksn": 4.0, "K0_6_branches": [0.396, 0.742],
                    "nucleation": {"seed003": 0.0166, "seed05": 0.7508}},
 "drift_phasor": {"cos": 0.0, "sin": "s - sqrt(s^2-1)", "perpendicular": True},
 "insight": "a=0 vs a=1 are different models; drifters contribute ZERO to R*"
}
with open('../outputs/reflexive_law_data.json','w') as f: json.dump(data, f, indent=2)
print("saved json")