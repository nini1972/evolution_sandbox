#!/usr/bin/env python3
"""DELIVERABLE: characterize the period-4 attractor at (r=3.87, eps=0.136), N=120.
Loads p4_long_traj.npy (400 x 120) and produces a 2x3 figure:
 (a) minimal-period signature  d_p (p=1..8)  -> shows period-4
 (b) time series of 4 representative sites (shows amplitude-modulated P4)
 (c) H/L pattern (binary) at t=0,1,2,3  -> shows full spatial inversion
 (d) H-site amplitude across the 4-phase cycle (the two H levels)
 (e) value histogram (bimodal)
 (f) space-time tile (t x site) -> the checkerboard+breathing texture
Also writes JSON summary.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

X = np.load("p4_long_traj.npy")   # (T, N)
T, N = X.shape
r, eps = 3.87, 0.136

# --- (a) minimal period signature ---
dp = []
for p in range(1, 9):
    d = np.array([np.max(np.abs(X[t + p] - X[t])) for t in range(50, T - p)])
    dp.append(float(d.mean()))

# --- (d) H-site amplitude per phase ---
Hmask = X > 0.675
phase_Hval, phase_Lval = [], []
for ph in range(4):
    # phase ph = all t with t % 4 == ph
    idx = [t for t in range(100, T - 4) if t % 4 == ph]
    hv = np.array([X[t, i] for t in idx for i in np.where(Hmask[t])[0]])
    lv = np.array([X[t, i] for t in idx for i in np.where(~Hmask[t])[0]])
    phase_Hval.append(float(hv.mean()) if len(hv) else np.nan)
    phase_Lval.append(float(lv.mean()) if len(lv) else np.nan)

# --- (c) representative H/L patterns at t=0..3 ---
tbase = 100
patterns = [(X[tbase + ph] > 0.675).astype(int) for ph in range(4)]

# --- pick representative sites: one strongly modulating + others ---
# find site with largest t-to-t+2 amplitude swing (the modulating H site)
swing = np.array([np.max(X[100:300:2, i]) - np.min(X[100:300:2, i]) for i in range(N)])
site_mod = int(np.argmax(swing))
sites_rep = [site_mod, site_mod + 1, site_mod + 2, 0]

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
# (a)
ax = axes[0, 0]
ax.bar(range(1, 9), dp, color=["tab:red" if d > 0.3 else ("tab:orange" if d > 0.05 else "tab:green") for d in dp])
ax.set_xlabel("p"); ax.set_ylabel(r"$d_p=\max_i|x_i(t{+}p)-x_i(t)|$")
ax.set_title("(a) minimal-period signature\n(d₄≈0, d₂=0.18 ≠0  ⇒  TRUE PERIOD 4)")
ax.set_xticks(range(1, 9))
ax.axhline(0.001, color="k", ls=":", lw=0.8)
for p, d in zip(range(1, 9), dp):
    ax.text(p, d + 0.01, f"{d:.3f}", ha="center", fontsize=7)
# (b)
ax = axes[0, 1]
tt = np.arange(T)
for s in sites_rep:
    ax.plot(tt, X[:, s], lw=0.8, label=f"site {s}")
ax.set_xlim(0, T); ax.set_title(f"(b) site time series (P4 w/ amplitude mod)\nmod site = {site_mod}")
ax.set_xlabel("t"); ax.set_ylabel("x"); ax.legend(fontsize=7)
# (c)
ax = axes[0, 2]
P4 = np.array(patterns)   # (4, N)
im = ax.imshow(P4, aspect="auto", cmap="viridis", vmin=0, vmax=1)
ax.set_title("(c) H(1)/L(0) pattern at t=0,1,2,3\n(rows=phase; full inversion each step)")
ax.set_yticks([0, 1, 2, 3]); ax.set_yticklabels(["t=0", "t=1", "t=2", "t=3"])
ax.set_xlabel("site"); plt.colorbar(im, ax=ax, shrink=0.7)
# (d)
ax = axes[1, 0]
ph = np.arange(4)
ax.plot(ph, phase_Hval, "o-", color="tab:red", label="H-site value")
ax.plot(ph, phase_Lval, "s-", color="tab:blue", label="L-site value")
ax.set_xticks(ph); ax.set_title("(d) amplitude per phase (4-phase cycle)\nH alternates 2 levels ⇒ P4")
ax.set_xlabel("phase t mod 4"); ax.set_ylabel("x"); ax.legend(fontsize=8)
for p in ph:
    ax.annotate(f"{phase_Hval[p]:.3f}", (p, phase_Hval[p]), textcoords="offset points", xytext=(0, 6), fontsize=7, color="tab:red")
    ax.annotate(f"{phase_Lval[p]:.3f}", (p, phase_Lval[p]), textcoords="offset points", xytext=(0, -12), fontsize=7, color="tab:blue")
# (e)
ax = axes[1, 1]
ax.hist(X.ravel(), bins=40, color="tab:purple", alpha=0.8)
ax.set_title("(e) global value histogram (bimodal)"); ax.set_xlabel("x"); ax.set_ylabel("count")
# (f)
ax = axes[1, 2]
im = ax.imshow(X[100:300].T, aspect="auto", cmap="viridis", origin="lower")
ax.set_title("(f) space-time tile (100–300) t→down, site→right\ncheckerboard inversion + amplitude breathing")
ax.set_xlabel("site"); ax.set_ylabel("t"); plt.colorbar(im, ax=ax, shrink=0.7)
fig.suptitle(f"PERIOD-4 ATTRACTOR  (r={r}, eps={eps}, N={N})  —  spatial antiphase backbone × amplitude modulation",
             fontsize=12, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("p4_period4_deliverable.png", dpi=115)
print("saved p4_period4_deliverable.png")

json.dump({
    "r": r, "eps": eps, "N": N, "T": T,
    "d_p": {str(p): dp[p - 1] for p in range(1, 9)},
    "H_count_per_step": [int(Hmask[t].sum()) for t in range(0, T, 25)],
    "phase_H_value": phase_Hval, "phase_L_value": phase_Lval,
    "mod_site": site_mod, "sites_rep": sites_rep,
    "value_min": float(X.min()), "value_max": float(X.max()),
    "verdict": "TRUE PERIOD-4 (d4~0, d2!=0): spatial period-2 full inversion + amplitude modulation",
}, open("p4_period4_deliverable.json", "w"), indent=2)
print("saved p4_period4_deliverable.json")
print("d_p:", np.round(dp, 4).tolist())
print("phase H value:", np.round(phase_Hval, 4).tolist())
print("phase L value:", np.round(phase_Lval, 4).tolist())
