#!/usr/bin/env python3
"""
IDENTIFY the P4 attractors at (r=3.87, eps=0.136), N=120.
Lock ~24 attractors, then:
  (1) visualize: 24 heatmaps (rows=sites, cols=4 time steps) + mean profiles
  (2) checkerboard test: e_i(t) = (-1)^i * x_i(t). If base state is a
      checkerboard modulated by a smooth spatial envelope, e(t) is SMOOTH
      (low dominant k, small high-k variance).
  (3) H/L domain structure: threshold at 0.675 -> binary sequence per t.
Save figure + JSON.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def f(x, r): return r * x * (1.0 - x)
def coupled(x, r, eps):
    fx = f(x, r)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def lock(r, eps, N, x0, trans=10000):
    x = x0.copy()
    for _ in range(trans):
        x = coupled(x, r, eps)
    P = np.empty((N, 4))
    for k in range(4):
        P[:, k] = x
        x = coupled(x, r, eps)
    return P

r, eps, N, NS = 3.87, 0.136, 120, 24
rng = np.random.default_rng(7)
Pats, kdom_raw, kdom_env, env_flat, hl_ratio, res4s = [], [], [], [], [], []
for i in range(NS):
    P = lock(r, eps, N, rng.random(N))
    Pats.append(P)
    res4s.append(float(np.max(np.abs(P - np.roll(P, 2, axis=1)))))
    # mean profile over time
    m = P.mean(axis=1)
    F = np.abs(np.fft.rfft(m - m.mean()))
    kdom_raw.append(int(np.argmax(F)) + 1)
    # checkerboard-unwrapped envelope
    sign = ((-1.0) ** np.arange(N)).reshape(N, 1)
    e = sign * P                              # N x 4
    me = e.mean(axis=1)
    Fe = np.abs(np.fft.rfft(me - me.mean()))
    kdom_env.append(int(np.argmax(Fe)) + 1)
    # envelope smoothness: fraction of FFT power in k <= 8
    tot = (Fe ** 2).sum() + 1e-30
    env_flat.append(float((Fe[:9] ** 2).sum() / tot))
    # H/L domain ratio per time step (fraction of sites > 0.675)
    hl_ratio.append([float((P[:, t] > 0.675).mean()) for t in range(4)])

Pats = np.array(Pats)
print("res4 (max |P-P2|) per attractor:", np.round(res4s, 12))
print("kdom_raw:", kdom_raw)
print("kdom_env (after checkerboard unwrap):", kdom_env)
print("env low-k power frac (smoothness):", np.round(env_flat, 3))
print("H-fraction per t (first 4 attractors):")
for h in hl_ratio[:4]:
    print("  ", np.round(h, 3))

# ---- Figure: 3 panels ----
fig, axes = plt.subplots(1, 3, figsize=(15, 10))
# (a) 24 attractors stacked as time series per site
ax = axes[0]
im = ax.imshow(Pats.reshape(N * NS, 4), aspect="auto", cmap="viridis")
for b in range(NS):
    ax.axhline(b * N - 0.5, color="w", lw=0.4)
ax.set_title(f"(a) 24 P4 attractors (rows=sites, x4 blocks; cols=t=0..3)\n(r={r}, eps={eps}, N={N})")
ax.set_yticks([b * N + N // 2 for b in range(NS)])
ax.set_yticklabels(range(NS), fontsize=6)
plt.colorbar(im, ax=ax, shrink=0.6)
# (b) mean spatial profiles
ax = axes[1]
xs = np.arange(N)
for i in range(NS):
    ax.plot(xs, Pats[i].mean(axis=1), lw=0.9)
ax.axhline(Pats.mean(), color="k", ls="--", lw=0.8)
ax.set_title("(b) mean spatial profile per attractor")
ax.set_xlabel("site"); ax.set_ylabel("<x_i(t)>_t")
# (c) checkerboard-unwrapped envelope
ax = axes[2]
for i in range(NS):
    ax.plot(xs, ((-1.0) ** xs) * Pats[i].mean(axis=1), lw=0.9)
ax.set_title("(c) envelope e_i = (-1)^i <x_i(t)> (smooth if checkerboard+envelope)")
ax.set_xlabel("site"); ax.set_ylabel("envelope")
fig.tight_layout()
fig.savefig("p4_family_visual.png", dpi=110)
print("saved p4_family_visual.png")

np.save("p4_attractors_24.npy", Pats)
import json
json.dump({"r": r, "eps": eps, "N": N, "nseeds": NS,
           "res4": res4s, "kdom_raw": kdom_raw, "kdom_env": kdom_env,
           "env_lowk_power": env_flat, "Hfrac_per_t": hl_ratio,
           "global_mean": float(Pats.mean()),
           "mean_std": float(Pats.std()),
           "kdom_raw_hist": {str(k): int((np.array(kdom_raw) == k).sum())
                              for k in np.unique(kdom_raw)},
           "kdom_env_hist": {str(k): int((np.array(kdom_env) == k).sum())
                              for k in np.unique(kdom_env)}},
          open("p4_family_visual.json", "w"), indent=2)
print("saved p4_family_visual.json, p4_attractors_24.npy")
