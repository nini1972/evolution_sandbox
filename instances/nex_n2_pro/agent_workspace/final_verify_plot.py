#!/usr/bin/env python3
"""FINAL VERIFICATION + FIGURE for the emergent multistable P4 checkerboard.

1. Nail the lock-window edges in eps (0.125, 0.128, 0.145, 0.148).
2. Checkerboard order parameter across seeds:
   C1 = <u_i u_{i+1}> / var(u)  (negative => antiphase neighbors).
3. Save profiles for plotting; render a 3-panel figure.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def coupled(x, r, eps):
    f = r*x*(1.0 - x)
    return (1.0 - eps)*f + (eps/2.0)*(np.roll(f,1) + np.roll(f,-1))

def run4(n, r, eps, trans, seed):
    np.random.seed(seed)
    x = np.random.rand(n)
    for _ in range(trans):
        x = coupled(x, r, eps)
    P = np.empty((n, 4))
    for k in range(4):
        P[:, k] = x
        x = coupled(x, r, eps)
    return P

r, n = 3.865, 120

# ---- 1. window edges ----
print("=== lock-window edges (exact s4 criterion, 120 cells) ===")
def frac_p4(eps, seed=0):
    np.random.seed(seed)
    x = np.random.rand(n)
    for _ in range(10000):
        x = coupled(x, r, eps)
    S = np.empty((40, n))
    for t in range(40):
        x = coupled(x, r, eps); S[t] = x
    c4 = 0
    for i in range(n):
        s4 = float(np.max(np.abs(S[4:, i] - S[:-4, i])))
        if s4 < 1e-9:
            c4 += 1
    return c4 / n

edges = []
for e in (0.12, 0.125, 0.128, 0.13, 0.132, 0.14, 0.145, 0.148, 0.15):
    f4 = frac_p4(e)
    edges.append((e, f4))
    print("  eps=%.4f  P4 fraction=%.3f" % (e, f4))

# ---- 2. checkerboard order parameter ----
print()
print("=== checkerboard order parameter C1 = <u_i u_{i+1}>/var  (3 seeds) ===")
C1s = []
for s in (0, 1, 2):
    P = run4(n, r, 0.132, 20000, s)
    u = P[:, 0].astype(float)
    u0 = u - u.mean()
    C1 = float(np.mean(u0 * np.roll(u0, 1)) / np.var(u))
    C1s.append(C1)
    print("  seed %d : C1=%.3f   (median|A-C|=%.2e)" % (s, C1, np.median(np.abs(P[:,0]-P[:,2]))))

# ---- 3. figure ----
np.savez("p4_profiles.npz",
         P0=run4(n, r, 0.132, 20000, 0),
         P1=run4(n, r, 0.132, 20000, 1),
         P2=run4(n, r, 0.132, 20000, 2),
         eps_edges=np.array([e for e, _ in edges]),
         p4frac=np.array([f for _, f in edges]),
         C1=np.array(C1s))

i = np.arange(n)
fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.4))

ax = axes[0]
cols = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd"]
for k in range(4):
    ax.plot(i, run4(n, r, 0.132, 20000, 0)[:, k], lw=1.0, alpha=0.85,
            color=cols[k], label="phase %d" % k)
ax.set_title("Seed-0: period-4 'breathing' of the frozen\ncheckerboard (4 temporal phases)", fontsize=10)
ax.set_xlabel("site i (120-ring)"); ax.set_ylabel("x_i"); ax.legend(fontsize=8)
ax.set_ylim(0, 1); ax.grid(alpha=0.3)

ax = axes[1]
for s, c in zip((0, 1, 2), cols[:3]):
    P = run4(n, r, 0.132, 20000, s)
    ax.plot(i, P[:, 0], lw=1.0, color=c, label="seed %d (C1=%.2f)" % (s, C1s[s]))
ax.set_title("Multistability: 3 initial conditions -> 3 distinct\nfrozen P4 envelopes (phase 0)", fontsize=10)
ax.set_xlabel("site i"); ax.set_ylabel("x_i"); ax.legend(fontsize=8)
ax.set_ylim(0, 1); ax.grid(alpha=0.3)

ax = axes[2]
ee = np.array([e for e, _ in edges]); ff = np.array([f for _, f in edges])
ax.plot(ee, ff, "-o", color="#8c564b", lw=1.4, ms=5)
ax.axhline(1.0, color="k", ls=":", lw=0.8)
ax.axhline(0.5, color="gray", ls=":", lw=0.8)
ax.set_title("Lock window in coupling eps at r=3.865\n(fraction of cells on exact P4)", fontsize=10)
ax.set_xlabel("eps (nearest-neighbor coupling)"); ax.set_ylabel("P4 fraction")
ax.set_xlim(0.115, 0.155); ax.set_ylim(-0.05, 1.1)
ax.grid(alpha=0.3)
ax.annotate("resonance\nwindow", xy=(0.136, 0.6), fontsize=9, ha="center", color="#8c564b")

fig.suptitle("Emergent multistable period-4 checkerboard in a weakly-coupled chaotic lattice "
             "(r=3.865)", fontsize=11, y=1.02)
fig.tight_layout()
fig.savefig("p4_checkerboard.png", dpi=150, bbox_inches="tight")
print()
print("saved p4_checkerboard.png")
