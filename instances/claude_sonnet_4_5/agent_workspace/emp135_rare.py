"""
EMP135_RARE — probe the rare high-C4 metastable state (random IC seed=1).
Questions: (1) spatial structure — uniform period-4 lock or domain state?
(2) does C4 survive FT surrogates? (3) does the h1-vs-h4 prediction test pass?
Treaty params r=3.865, eps=0.132, N=100; longer run T=6000, burn=1500.
"""
import numpy as np, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = "emp135_rare"
os.makedirs(OUT, exist_ok=True)

R, EPS, N, T, BURN = 3.865, 0.132, 100, 6000, 1500


def run(seed, ic='random', T=T, burn=BURN):
    rng = np.random.default_rng(seed)
    if ic == 'random':
        x = rng.uniform(0.1, 0.9, N)
    else:
        x = np.full(N, 0.2)
    traj = []
    for t in range(T):
        xm, xp = np.roll(x, 1), np.roll(x, -1)
        x = (1 - EPS) * R * x * (1 - x) + EPS * 0.5 * (R * xm * (1 - xm) + R * xp * (1 - xp))
        x = np.where(np.isfinite(x), x, 0.0)
        x = np.clip(x, -1e6, 1e6)
        if t >= burn:
            traj.append(x.copy())
    return np.array(traj)


def acf(seq, maxlag):
    seq = np.asarray(seq, float); seq = seq - seq.mean()
    v = np.dot(seq, seq)
    if v <= 0:
        return np.zeros(maxlag + 1)
    return np.array([np.dot(seq[:len(seq) - k], seq[k:]) / v for k in range(maxlag + 1)])


def c4_residues(ac):
    lags = np.arange(1, len(ac))
    res = {r4: float(np.mean(ac[lags[lags % 4 == r4]])) for r4 in range(4)}
    return res, res[0] - res[2]


def ft_surrogate(x, seed):
    rng = np.random.default_rng(seed)
    n = len(x)
    F = np.fft.rfft(x - x.mean())
    ph = rng.uniform(0, 2 * np.pi, len(F)); ph[0] = 0.0
    if n % 2 == 0:
        ph[-1] = 0.0
    return np.fft.irfft(np.abs(F) * np.exp(1j * ph), n=n)


def local_pred(series, H, tau, w, emb, k):
    n = len(series)
    m = n - (emb - 1) * tau - H
    E = np.column_stack([series[j * tau: j * tau + m] for j in range(emb)])
    tgt1 = series[(emb - 1) * tau: (emb - 1) * tau + m]
    tgtH = series[(emb - 1) * tau + H: (emb - 1) * tau + H + m]
    dmat = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)
    np.fill_diagonal(dmat, np.inf)
    idx_all = np.argsort(dmat, axis=1)
    errs = []
    for i in range(m):
        cand = [j for j in idx_all[i] if abs(j - i) > w][:k]
        wts = 1.0 / (dmat[i, cand] + 1e-12); wts /= wts.sum()
        errs.append((np.dot(wts, tgt1[cand]) - tgt1[i], np.dot(wts, tgtH[cand]) - tgtH[i]))
    errs = np.array(errs)
    return (float(np.mean(errs[:, 0] ** 2) / (np.var(tgt1) + 1e-12)),
            float(np.mean(errs[:, 1] ** 2) / (np.var(tgtH) + 1e-12)))


report = {}
print("=== screen seeds for high-C4 state (T=6000, burn=1500) ===")
target_seed = None
for seed in range(6):
    traj = run(seed)
    s = traj.mean(axis=1)
    _, C4 = c4_residues(acf(s, 40))
    print(f"  seed={seed}: C4={C4:+.3f}  mean|s|={np.mean(np.abs(s)):.3f}")
    if abs(C4) > 0.1 and target_seed is None:
        target_seed = seed
if target_seed is None:
    target_seed = 1  # from earlier sweep
print(f"probing seed={target_seed}")

traj = run(target_seed)
s = traj.mean(axis=1)
res, C4 = c4_residues(acf(s, 40))
print(f"\nprobe seed={target_seed}: C4={C4:+.3f}, residues={ {k: round(v,3) for k,v in res.items()} }")

# (1) spatial structure: per-site lag-4 autocorrelation + period detection
site_c4, site_dom = [], []
for j in range(N):
    sj = traj[:, j]
    _, c = c4_residues(acf(sj, 40))
    site_c4.append(c)
    # dominant period from ACF peaks
    ac = acf(sj, 40)
    site_dom.append(int(np.argmax(ac[1:40])) + 1)
site_c4 = np.array(site_c4)
frac_homog = float(np.mean(traj.std(axis=1) < 1e-6))  # fraction of times spatially uniform
print(f"spatial: site C4 mean={site_c4.mean():+.3f}±{site_c4.std():.3f}, "
      f"frac sites |C4|>0.1: {np.mean(np.abs(site_c4)>0.1):.2f}, "
      f"spatial-uniform frac={frac_homog:.3f}")
print(f"  dominant lag histogram: {dict(zip(*np.unique(site_dom, return_counts=True)))}")

# (2) FT surrogate discrimination on spatial mean
C4_sur = np.array([c4_residues(acf(ft_surrogate(s, 5000 + i), 40))[1] for i in range(80)])
z = (C4 - C4_sur.mean()) / (C4_sur.std() + 1e-12)
print(f"\nFT-surrogate: real C4={C4:+.3f} vs sur {C4_sur.mean():+.3f}±{C4_sur.std():.3f} z={z:+.2f}")

# (3) prediction test
e1, e4 = local_pred(s[:2500], 4, 1, 100, emb=6, k=6)
gain = (e1 - e4) / e1
sur_gain = np.array([(lambda ab: (ab[0]-ab[1])/ab[0])(
    local_pred(ft_surrogate(s[:2500], 7000+i), 4, 1, 100, emb=6, k=6)) for i in range(8)])
z_gain = (gain - sur_gain.mean()) / (sur_gain.std() + 1e-12)
print(f"prediction: h1={e1:.4f} h4={e4:.4f} gain={gain*100:+.1f}% z={z_gain:+.2f} "
      f"(FT-sur gain {sur_gain.mean()*100:+.1f}±{sur_gain.std()*100:.1f}%)")

report = dict(target_seed=target_seed, C4=float(C4), residues=res,
              site_c4_mean=float(site_c4.mean()), site_c4_std=float(site_c4.std()),
              frac_sites_hit=float(np.mean(np.abs(site_c4) > 0.1)),
              spatial_uniform_frac=frac_homog,
              C4_sur_mean=float(C4_sur.mean()), C4_sur_std=float(C4_sur.std()), z=float(z),
              e1=e1, e4=e4, gain=gain, gain_sur_mean=float(sur_gain.mean()),
              gain_sur_std=float(sur_gain.std()), z_gain=float(z_gain))

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
ax = axes[0]
im = ax.imshow(traj[:300].T, aspect='auto', cmap='viridis', interpolation='nearest')
ax.set_title(f"space-time (seed {target_seed})"); ax.set_xlabel("t"); ax.set_ylabel("site")
plt.colorbar(im, ax=ax, fraction=0.046)
ax = axes[1]
ax.hist(C4_sur, bins=20, alpha=0.75, color="#a6bddb", label="FT surrogates")
ax.axvline(C4, color='red', lw=2, label=f"real C4={C4:.3f}")
ax.legend(fontsize=8); ax.set_title(f"C4 under FT surrogates (z={z:+.2f})")
ax = axes[2]
ax.bar(["h=1", "h=4"], [e1, e4], color=["#969696", "#e34a33"])
ax.set_title(f"pred error: gain {gain*100:+.1f}%, z={z_gain:+.2f}")
ax.set_ylabel("norm MSE")
fig.tight_layout()
fig.savefig(f"{OUT}/emp135_rare_probe.png", dpi=110)
with open(f"{OUT}/emp135_rare_probe.json", "w") as f:
    json.dump(report, f, indent=2, default=float)
print("\nREPORT:", json.dumps(report, indent=2, default=float))
