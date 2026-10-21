"""
EMP135_BASIN — characterize the rare high-C4 state found for random IC seed=1:
(a) time-resolved windowed C4 over 2e5 steps: onset, growth, decay?
(b) basin fraction over 30 random ICs (T=6000, burn=1500)
(c) perturbation response: is it a robust attractor or fragile transient?
Treaty params: r=3.865, eps=0.132, N=100, additive periodic coupling.
"""
import numpy as np, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = "emp135_basin"
os.makedirs(OUT, exist_ok=True)

R, EPS, N = 3.865, 0.132, 100


def run(x0, T, burn=0, noise=0.0, seed=None, mean_only=False):
    rng = np.random.default_rng(seed)
    x = x0.copy().astype(float)
    traj = []
    for t in range(T):
        xm, xp = np.roll(x, 1), np.roll(x, -1)
        x = (1 - EPS) * R * x * (1 - x) + EPS * 0.5 * (R * xm * (1 - xm) + R * xp * (1 - xp))
        if noise > 0:
            x = x + noise * rng.normal(size=N)
        x = np.where(np.isfinite(x), x, 0.0)
        x = np.clip(x, -1e6, 1e6)
        if t >= burn:
            traj.append(float(x.mean()) if mean_only else x.copy())
    return np.array(traj)


def c4_of(seq):
    seq = np.asarray(seq, float); seq = seq - seq.mean()
    v = np.dot(seq, seq)
    if v <= 0:
        return 0.0
    ac = np.array([np.dot(seq[:len(seq) - k], seq[k:]) / v for k in range(41)])
    lags = np.arange(1, 41)
    return float(np.mean(ac[lags[lags % 4 == 0]]) - np.mean(ac[lags[lags % 4 == 2]]))


# ---- (a) time-resolved C4, seed=1, T=200000 ---------------------------------
T = 200000
x0 = np.random.default_rng(1).uniform(0.1, 0.9, N)
s = run(x0, T, mean_only=True)
W = 500
c4_series = [c4_of(s[i:i + 4 * W]) for i in range(0, len(s) - 4 * W, W)]
t_axis = np.arange(len(c4_series)) * W
onset = t_axis[np.argmax(np.array(c4_series) > 0.1)] if max(c4_series) > 0.1 else None
print(f"(a) seed=1, T={T}: C4 windows min={min(c4_series):+.3f} max={max(c4_series):+.3f} "
      f"final={c4_series[-1]:+.3f} onset≈t={onset}")

# ---- (b) basin fraction -----------------------------------------------------
hits, finals = 0, []
NB = 30
for k in range(NB):
    xk = np.random.default_rng(1000 + k).uniform(0.1, 0.9, N)
    tk = run(xk, 6000, burn=1500)
    c = c4_of(tk.mean(axis=1))
    finals.append(c)
    if c > 0.1:
        hits += 1
print(f"(b) basin: {hits}/{NB} random ICs reach C4>0.1; finals="
      f"{np.round(np.array(finals),2).tolist()}")

# ---- (c) perturbation of the high-C4 state ---------------------------------
x1 = x0.copy()
# let it evolve 6000, then kick
tmp = run(x1, 6000, burn=0)
x1 = tmp[-1]
base = c4_of(run(x1, 8000).mean(axis=1))
res = {}
for amp in [1e-6, 1e-3, 0.05]:
    rk = np.random.default_rng(42)
    xk = x1 + amp * rk.normal(size=N)
    ck = c4_of(run(xk, 8000).mean(axis=1))
    res[str(amp)] = ck
    print(f"(c) kick amp={amp:g}: post-kick C4={ck:+.3f}")
print(f"(c) unperturbed continuation C4={base:+.3f}")

# ---- noise robustness -------------------------------------------------------
noise_res = {}
for nu in [1e-6, 1e-4, 1e-3]:
    ck = c4_of(run(x1, 8000, noise=nu, seed=7).mean(axis=1))
    noise_res[str(nu)] = ck
    print(f"noise={nu:g}: C4={ck:+.3f}")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].plot(t_axis, c4_series, color="#2b8cbe")
axes[0].axhline(0.1, color='gray', ls=':')
axes[0].axhline(0.257, color='green', ls='--', label='treaty 0.257')
axes[0].set_xlabel('t'); axes[0].set_ylabel('windowed C4')
axes[0].set_title('(a) C4 vs time (seed=1)'); axes[0].legend(fontsize=8)
axes[1].hist(finals, bins=15, color="#a6bddb", edgecolor='k')
axes[1].axvline(0.1, color='red', ls='--'); axes[1].axvline(0.257, color='green', ls='--')
axes[1].set_title(f'(b) basin finals ({hits}/{NB} hit)'); axes[1].set_xlabel('C4')
lbls = ['unpert'] + [f'kick {k}' for k in res] + [f'noise {k}' for k in noise_res]
vals = [base] + list(res.values()) + list(noise_res.values())
axes[2].bar(range(len(vals)), vals, color="#fdae6b")
axes[2].set_xticks(range(len(vals))); axes[2].set_xticklabels(lbls, rotation=45, ha='right', fontsize=7)
axes[2].set_title('(c) perturbation robustness'); axes[2].set_ylabel('post C4')
fig.tight_layout()
fig.savefig(f"{OUT}/emp135_basin.png", dpi=110)
rep = dict(time_trace=dict(min=min(c4_series), max=max(c4_series), final=c4_series[-1], onset=onset),
           basin_hits=hits, basin_total=NB, basin_finals=[float(f) for f in finals],
           unpert=base, kicks=res, noise=noise_res)
with open(f"{OUT}/emp135_basin.json", "w") as f:
    json.dump(rep, f, indent=2, default=float)
print("saved", OUT)