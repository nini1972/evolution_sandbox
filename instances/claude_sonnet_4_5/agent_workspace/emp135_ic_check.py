"""
EMP135_IC_CHECK — pre-dossier robustness: does the treaty C4=0.257 depend on
initial condition or burn-in? Cheap local sweep, treaty params
(r=3.865, eps=0.132, N=100, T=2000).
"""
import numpy as np, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = "emp135_ic_check"
os.makedirs(OUT, exist_ok=True)

R, EPS, N, T = 3.865, 0.132, 100, 2000


def run(x0_kind, seed, burn=0, bc='periodic', form='additive'):
    rng = np.random.default_rng(seed)
    if x0_kind == 'uniform02':
        x = np.full(N, 0.2)
    elif x0_kind == 'uniform05':
        x = np.full(N, 0.5)
    elif x0_kind == 'random':
        x = rng.uniform(0.1, 0.9, N)
    elif x0_kind == 'delta':
        x = np.full(N, 0.2); x[N // 2] = 0.7
    elif x0_kind == 'noise05':
        x = 0.5 + 0.05 * rng.normal(size=N)
    elif x0_kind == 'checker':
        x = np.where(np.arange(N) % 2 == 0, 0.3, 0.7)
    traj = []
    for t in range(T):
        if bc == 'periodic':
            xm, xp = np.roll(x, 1), np.roll(x, -1)
        else:
            xm = np.empty(N); xp = np.empty(N)
            xm[1:] = x[:-1]; xm[0] = x[0]
            xp[:-1] = x[1:]; xp[-1] = x[-1]
        if form == 'additive':
            x = (1 - EPS) * R * x * (1 - x) + EPS * 0.5 * (R * xm * (1 - xm) + R * xp * (1 - xp))
        else:
            y = (1 - EPS) * x + EPS * 0.5 * (xm + xp)
            x = R * y * (1 - y)
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


def C4(ac):
    lags = np.arange(1, len(ac))
    m0 = np.mean(ac[lags[lags % 4 == 0]])
    m2 = np.mean(ac[lags[lags % 4 == 2]])
    return float(m0 - m2)


rows = []
print(f"{'IC':10s} {'seed':4s} {'burn':5s} {'div':5s} {'C4_full':>8s} {'C4_tail':>8s} {'mean|s|':>8s}")
for ic in ['uniform02', 'uniform05', 'random', 'delta', 'noise05', 'checker']:
    for seed in [0, 1, 2]:
        for burn in [0, 500, 1500]:
            traj = run(ic, seed, burn=burn)
            s = traj.mean(axis=1)
            div = bool(np.any(np.abs(s) > 1e3))
            c4_full = C4(acf(s, 40))
            # tail window (last 60% of series) — tests stationarity dependence
            tail = s[int(0.4 * len(s)):]
            c4_tail = C4(acf(tail, 40)) if len(tail) > 100 else float('nan')
            rows.append(dict(ic=ic, seed=seed, burn=burn, div=div,
                             c4_full=c4_full, c4_tail=c4_tail,
                             mean_abs=float(np.mean(np.abs(s)))))
            print(f"{ic:10s} {seed:<4d} {burn:<5d} {str(div):5s} {c4_full:+8.3f} {c4_tail:+8.3f} {np.mean(np.abs(s)):8.3f}")

c4s = [r['c4_full'] for r in rows if not r['div']]
c4t = [r['c4_tail'] for r in rows if not r['div']]
print(f"\nacross {len(c4s)} stable configs: C4_full in [{min(c4s):.3f}, {max(c4s):.3f}], "
      f"mean={np.mean(c4s):+.3f}±{np.std(c4s):.3f}")
print(f"                          C4_tail in [{min(c4t):.3f}, {max(c4t):.3f}], "
      f"mean={np.mean(c4t):+.3f}±{np.std(c4t):.3f}")
print(f"treaty target = 0.257 (threshold 0.1); "
      f"configs with |C4|>0.1: {sum(1 for c in c4s if abs(c) > 0.1)}/{len(c4s)}")

fig, ax = plt.subplots(figsize=(10, 5))
stable = [r for r in rows if not r['div']]
ax.scatter(range(len(stable)), [r['c4_full'] for r in stable], label='C4 full', color='#2b8cbe')
ax.scatter(range(len(stable)), [r['c4_tail'] for r in stable], label='C4 tail(60%)', color='#e34a33', marker='x')
ax.axhline(0.257, color='green', ls='--', label='treaty C4=0.257')
ax.axhline(0.1, color='gray', ls=':', label='threshold 0.1')
ax.axhline(-0.1, color='gray', ls=':')
ax.set_ylim(-0.5, 0.5)
ax.set_xlabel('config index (IC × seed × burn)')
ax.set_ylabel('C4 residue')
ax.set_title('EMP135 IC/burn-in robustness sweep (treaty params)')
ax.legend()
fig.tight_layout()
fig.savefig(f"{OUT}/emp135_ic_check.png", dpi=110)
with open(f"{OUT}/emp135_ic_check.json", "w") as f:
    json.dump(rows, f, indent=2, default=float)
print(f"saved {OUT}/emp135_ic_check.png + .json")
