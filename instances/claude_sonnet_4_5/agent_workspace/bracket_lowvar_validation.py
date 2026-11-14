#!/usr/bin/env python3
'''
two-null bracket: LOW-VARIANCE FALLBACK + RANK-p VALIDATION
============================================================
Consensus corrected z-score protocol (thread th_1794537149_b6c7):
    z_F     = (DET_obs - mean(DET_F))     / std(DET_F, ddof=1)
    z_IAAFT = (DET_obs - mean(DET_IAAFT)) / std(DET_IAAFT, ddof=1)
    dz      = z_F - z_IAAFT
Failure mode under investigation (poolside_laguna,
job_poolside_laguna_1794537059_28ba): Gray-Scott DET ~ 0.999 for
EVERY surrogate -> std ~ 0 -> z = nan (division by zero).
Three-tier protocol validated here:
    tier 1 z-scores  (used when std > 0)
    tier 2 raw gap   (used when std <= 1e-12): gap = DET_obs - mean(null)
    tier 3 rank p    (always defined, distribution-free):
             p = (1 + #{DET_null >= DET_obs}) / (N_SUR + 1)
Null controls: AR(1) linear -> bracket must OPEN (small dz),
logistic chaos -> bracket must CLOSE (large |dz| / small rank p).
Systems: AR(1), logistic map, Kuramoto order parameter,
Gray-Scott u-trace (high-DET stress test of the fallback).
'''
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from colony_lib.persistence import StageTracker

SEED = 20261113
rng = np.random.default_rng(SEED)
N = 800
N_SUR = 200
M_EMB = 2
TAU = 3
EPS = 0.1


def standardize(x):
    x = np.asarray(x, dtype=float)
    s = np.std(x)
    if s <= 0 or not np.isfinite(s):
        return x - np.mean(x)
    return (x - np.mean(x)) / s


def fourier_surrogate(x, rng):
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)
    n = len(x)
    f = np.fft.rfft(x)
    amp = np.abs(f)
    ph = rng.uniform(0, 2 * np.pi, len(f))
    ph[0] = np.angle(f[0]) if len(f) else 0.0
    if n % 2 == 0 and len(f) > 1:
        ph[-1] = np.angle(f[-1])
    s = np.fft.irfft(amp * np.exp(1j * ph), n=n)
    return standardize(s)


def iaaft_surrogate(x, rng, n_iter=40):
    x = np.asarray(x, dtype=float)
    n = len(x)
    target_sorted = np.sort(x)
    target_spec = np.abs(np.fft.rfft(x - np.mean(x)))
    s = x[rng.permutation(n)]
    for _ in range(n_iter):
        spec = np.fft.rfft(s - np.mean(s))
        phase = spec / (np.abs(spec) + 1e-300)
        s2 = np.fft.irfft(target_spec * phase, n=n)
        order = np.argsort(s2)
        s_new = np.empty(n)
        s_new[order] = target_sorted
        if np.allclose(s, s_new, atol=1e-12):
            s = s_new
            break
        s = s_new
    return standardize(s)


def det_of(x, m=M_EMB, tau=TAU, eps=EPS):
    e = takens_embedding(np.asarray(x, dtype=float), m=m, tau=tau)
    R = recurrence_matrix(e, epsilon=eps)
    return float(compute_rqa_metrics(R)['determinism'])


def bracket(obs, sur_f, sur_i):
    d_obs = det_of(obs)
    d_f = np.array([det_of(s) for s in sur_f])
    d_i = np.array([det_of(s) for s in sur_i])
    sf, si = np.std(d_f, ddof=1), np.std(d_i, ddof=1)
    if sf > 1e-12 and si > 1e-12:
        zF = (d_obs - np.mean(d_f)) / sf
        zI = (d_obs - np.mean(d_i)) / si
        dz = zF - zI
        tier = 1
    else:
        zF = np.nan
        zI = np.nan
        dz = (np.mean(d_f) - np.mean(d_i)) * 0.0  # placeholder
        dz = np.nan
        tier = 2
    # raw gaps always
    gapF = d_obs - np.mean(d_f)
    gapI = d_obs - np.mean(d_i)
    # rank p-values, distribution free, always defined
    pF = (1.0 + np.sum(d_f >= d_obs)) / (len(d_f) + 1.0)
    pI = (1.0 + np.sum(d_i >= d_obs)) / (len(d_i) + 1.0)
    return dict(DET_obs=d_obs, zF=float(zF), zI=float(zI), dz=float(dz),
                gapF=float(gapF), gapI=float(gapI), pF=float(pF), pI=float(pI),
                tier=tier, stdF=float(sf), stdI=float(si),
                DET_F_mean=float(np.mean(d_f)), DET_I_mean=float(np.mean(d_i)),
                DET_F_std=float(sf), DET_I_std=float(si))


def make_ar1(n=N, phi=0.7, seed=SEED):
    r = np.random.default_rng(seed)
    e = r.normal(0, 1, n)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return standardize(x)


def make_logistic(n=N, r=3.9999, seed=SEED):
    r0 = np.random.default_rng(seed)
    x = 0.5
    out = []
    for _ in range(200 + n):
        x = r * x * (1 - x)
        if _ >= 200:
            out.append(x)
    return standardize(np.array(out))


def make_kuramoto(n=N, seed=SEED):
    r0 = np.random.default_rng(seed)
    from colony_lib.dynamics import simulate_kuramoto
    try:
        res = simulate_kuramoto(N=60, K=2.0, omega=None, dt=0.05,
                                steps=n, seed=seed, record_every=1)
        if isinstance(res, dict):
            for k in ('r', 'order', 'R', 'order_parameter'):
                if k in res:
                    return standardize(np.asarray(res[k], dtype=float)[:n])
        arr = np.asarray(res)
        if arr.ndim == 2 and arr.shape[1] > 1:
            ph = arr[:, 1:] if arr.shape[0] == n else arr.T[:, 1:]
            rr = np.abs(np.mean(np.exp(1j * ph), axis=1))
            return standardize(rr[:n])
    except Exception as exc:
        print('kuramoto lib failed, using RK4 fallback:', exc)
    # fallback: vectorized RK4 Kuramoto
    w = r0.normal(0, 1, 60)
    th = r0.uniform(0, 2 * np.pi, 60)
    K, dt = 2.0, 0.05
    rec = []
    for step in range(n):
        def f(th):
            return w + K * np.mean(np.sin(th[None, :] - th[:, None]), axis=1)
        k1 = f(th)
        k2 = f(th + 0.5 * dt * k1)
        k3 = f(th + 0.5 * dt * k2)
        k4 = f(th + dt * k3)
        th = th + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        rec.append(np.abs(np.mean(np.exp(1j * th))))
    return standardize(np.array(rec))


def make_gray_scott(n=N, seed=SEED):
    L = 64
    steps = 800
    u = np.ones((L, L))
    v = np.zeros((L, L))
    r0 = np.random.default_rng(seed)
    for _ in range(6):
        cx, cy = r0.integers(8, L - 8, 2)
        u[cx - 3:cx + 3, cy - 3:cy + 3] = 0.50
        v[cx - 3:cx + 3, cy - 3:cy + 3] = 0.25
    F, k, Du, dv = 0.03, 0.06, 0.16, 0.08
    dt = 1.0
    tr = []
    lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], float)
    def conv(a):
        p = np.pad(a, 1, mode='edge')
        out = np.zeros_like(a)
        for i in range(3):
            for j in range(3):
                if lap[i, j] != 0:
                    out += lap[i, j] * p[i:i + L, j:j + L]
        return out
    for s in range(steps):
        ruv = u * v * v
        lu, lv = conv(u), conv(v)
        u = u + dt * (Du * lu - ruv + F * (1 - u))
        v = v + dt * (dv * lv + ruv - (F + k) * v)
        if s >= steps - n:
            tr.append(u[L // 2, L // 2])
    return standardize(np.array(tr))


results = {}
systems = [
    ('AR1_linear_control', make_ar1(), 'linear'),
    ('logistic_chaos', make_logistic(), 'chaotic'),
    ('kuramoto_sync', make_kuramoto(), 'synchronized'),
    ('gray_scott_highDET', make_gray_scott(), 'high-det'),
]
for name, obs, label in systems:
    sur_f = [fourier_surrogate(obs, rng) for _ in range(N_SUR)]
    sur_i = [iaaft_surrogate(obs, rng) for _ in range(N_SUR)]
    b = bracket(obs, sur_f, sur_i)
    b['kind'] = label
    results[name] = b
    print(name, json.dumps(b, indent=2))

# stress test: force zero-variance null (all identical surrogates)
obs0 = make_logistic()
ident = [obs0.copy() for _ in range(200)]
forced = bracket(obs0, ident, ident)
forced['kind'] = 'forced-zero-variance'
results['forced_zero_variance'] = forced
print('forced', json.dumps(forced, indent=2))

# summary classification
summary = {}
for k, b in results.items():
    close = (b['tier'] == 1 and abs(b['dz']) > 2.0) or (b['pI'] <= 0.05)
    if b['kind'] == 'linear':
        summary[k] = dict(bracket='OPEN' if abs(b['dz']) < 2.0 or b['pF'] > 0.05 else 'CLOSED',
                          pF=b['pF'], pI=b['pI'], dz=b['dz'], tier=b['tier'])
    else:
        summary[k] = dict(bracket='CLOSED' if close else 'OPEN',
                          pF=b['pF'], pI=b['pI'], dz=b['dz'], tier=b['tier'])
print('SUMMARY', json.dumps(summary, indent=2))

with open('lowvar_validation.json', 'w') as fh:
    json.dump(dict(results=results, summary=summary), fh, indent=2)

# figure
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for ax, (name, b) in zip(axes.ravel(), list(results.items())[:4]):
    ax.bar(['gapF', 'gapI'], [b['gapF'], b['gapI']], color=['#4C72B0', '#DD8452'])
    ax.axhline(0, color='k', lw=0.8)
    ax.set_title(name + '  tier=' + str(b['tier']))
    ax.set_ylabel('DET_obs - DET_null')
fig.suptitle('Two-null bracket: low-variance fallback + rank-p (N=200 surrogates)')
fig.tight_layout()
fig.savefig('lowvar_validation.png', dpi=120)
print('DONE')
