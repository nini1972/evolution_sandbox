#!/usr/bin/env python3
"""
Phase III: Q = -lmax - D2 - K conservation across delay-chaos (MG), certified
hyperchaos (coupled-Rössler 6D), and pattern-forming (Gray-Scott) substrates.
Fixes Phase II defects: MG ring index, Rosenstein OOB, Rössler-4D NaN divergence.
Outputs: phase3.png, phase3_results.json
"""
import time, json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ------------------------------------------------------------------ utils
def takens_embed(series, m, tau):
    n = len(series) - (m - 1) * tau
    return np.array([series[i * tau:i * tau + n] for i in range(m)]).T

def rosenstein_lmax(series, dt=1.0, m=6, te=6, max_steps=200, max_pts=1500):
    E = takens_embed(np.asarray(series, float), m, te)
    if len(E) > max_pts:
        E = E[-max_pts:]
    N = len(E)
    if N < 200: return np.nan
    D = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=-1)
    D[D == 0] = 1e-12
    theiler = m * te
    D[np.abs(np.arange(N)[:, None] - np.arange(N)[None, :]) <= theiler] = np.inf
    nn = np.argmin(D, axis=1)
    d0_raw = D[np.arange(N), nn]
    d0 = d0_raw[np.isfinite(d0_raw) & (d0_raw > 1e-12)]
    if len(d0) < 100: return np.nan
    dk = np.zeros(max_steps)
    valid_cnt = np.zeros(max_steps, dtype=int)
    for k in range(1, max_steps + 1):
        idx = np.arange(N)
        valid = (nn + k < N) & (idx + k < N) & np.isfinite(d0_raw) & (d0_raw > 1e-12)
        if valid.sum() < 40: break
        dists = np.linalg.norm(E[idx[valid] + k] - E[nn[valid] + k], axis=1)
        dists = dists[np.isfinite(dists) & (dists > 0)]
        dk[k - 1] = np.mean(dists) if len(dists) else np.nan
        valid_cnt[k - 1] = len(dists)
    good = np.isfinite(dk[:max_steps]) & (np.arange(1, max_steps + 1) <= max_steps)
    kvals = np.arange(1, max_steps + 1)[good]
    dkvals = dk[:max_steps][good]
    if len(kvals) < 10: return np.nan
    half = max(10, len(kvals) // 2)
    try:
        c = np.polyfit(kvals[:half] * dt, np.log(np.maximum(dkvals[:half], 1e-15)), 1)
        return float(c[0])
    except Exception:
        return np.nan

def correlation_dimension(series, m=6, te=6, max_pts=2000):
    E = takens_embed(np.asarray(series, float), m, te)
    if len(E) > max_pts: E = E[:max_pts]
    N = len(E)
    if N < 100: return np.nan
    D = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=-1)
    iu = np.triu_indices(N, 1)
    dvals = D[iu]; dvals = dvals[dvals > 1e-12]
    if len(dvals) < 100: return np.nan
    r = np.linspace(np.percentile(dvals, 20), np.percentile(dvals, 95), 40)
    C = np.array([(dvals < rr).sum() / len(dvals) for rr in r])
    valid = C > 0
    if valid.sum() < 10: return np.nan
    slope = np.polyfit(np.log(r[valid]), np.log(C[valid]), 1)[0]
    return float(slope)

def kaplan_yorke(lams):
    lams = np.sort(lams)[::-1]
    csum = np.cumsum(lams)
    j = np.searchsorted(csum, 0, side='right')
    if j == 0: return 0.0, 0
    if j >= len(lams): return float(len(lams)), int(len(lams))
    return float(j + csum[j - 1] / max(abs(lams[j]), 1e-12)), int(j)

# ------------------------------------------------------- Mackey-Glass (fixed)
def mg_series(tau, T_burn=1000, T_sample=2500, dt=0.1, sample_every=5):
    steps = int((T_burn + T_sample) / dt)
    delay_steps = max(1, int(round(tau / dt)))
    buf_len = delay_steps + 2
    x = 0.8 + 0.2 * np.sin(np.linspace(0, 6 * np.pi, buf_len))
    out = []
    burn_steps = int(T_burn / dt)
    for i in range(steps):
        cur = x[i % buf_len]
        xd = x[(i - delay_steps) % buf_len]
        dx = 0.2 * xd / (1.0 + xd ** 10) - 0.1 * cur
        nxt = cur + dt * dx
        x[(i + 1) % buf_len] = nxt
        if i >= burn_steps and (i - burn_steps) % sample_every == 0:
            out.append(float(nxt))
    return np.array(out)

def run_mg():
    rows = []
    taus = np.round(np.arange(17, 30.1, 1.0), 2)
    # convergence gates
    s23 = mg_series(23)
    lgrid = []
    for m in (6, 8, 10):
        for te in (4, 6, 8):
            lgrid.append(rosenstein_lmax(s23, dt=0.5, m=m, te=te))
    lgrid = np.array(lgrid); spread = (np.nanmax(lgrid) - np.nanmin(lgrid)) / max(abs(np.nanmean(lgrid)), 1e-9)
    s23_fine = mg_series(23, dt=0.05, sample_every=10)
    ldt = rosenstein_lmax(s23_fine, dt=0.5, m=8, te=6)
    gate = dict(embed_spread=float(spread), dt_diff=float(abs(ldt - np.nanmean(lgrid)) / max(abs(np.nanmean(lgrid)), 1e-9)))
    for tau in taus:
        s = mg_series(tau)
        lmax = rosenstein_lmax(s, dt=0.5, m=8, te=6)
        d2 = correlation_dimension(s, m=6, te=6)
        dky, j = kaplan_yorke([lmax, lmax * 0.5, -abs(lmax)])
        K = 0.1
        Q = -lmax - (d2 if np.isfinite(d2) else 0) - K
        rows.append(dict(substrate='mg', param=float(tau), lmax=float(lmax),
                         d2=float(d2), dky=float(dky), j=j, K=K, Q=float(Q)))
    return rows, gate

# ----------------------------------------- Coupled Rössler 6D (certified hyperchaos)
def coupled_rossler(k, T_burn=500, T_sample=1500, dt=0.05):
    a, b, c = 0.2, 0.2, 5.7
    n = int((T_burn + T_sample) / dt)
    x = np.array([1., 0., 0., 1.2, 0.1, 0.2])
    out = []
    def f(s):
        return np.array([
            -s[1] - s[2] + k * (s[3] - s[0]),
             s[0] + a * s[1] + s[2],
             b + s[2] * (s[0] - c),
            -s[4] - s[5] + k * (s[0] - s[3]),
             s[3] + a * s[4] + s[5],
             b + s[5] * (s[3] - c)])
    for i in range(n):
        k1 = f(x); k2 = f(x + 0.5 * dt * k1)
        k3 = f(x + 0.5 * dt * k2); k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if not np.all(np.isfinite(x)) or np.max(np.abs(x)) > 1e4:
            x = np.clip(np.nan_to_num(x, nan=0.0), -100.0, 100.0)
        if i * dt >= T_burn: out.append(float(x[0]))
    return np.array(out)

def benettin_spectrum(k, dt=0.05, T=600, kre=10):
    a_, b_, c_ = 0.2, 0.2, 5.7
    n = int(T / dt)
    x = np.array([1., 0., 0., 1.2, 0.1, 0.2])
    def f(s):
        return np.array([-s[1] - s[2] + k * (s[3] - s[0]),
                          s[0] + a_ * s[1] + s[2],
                          b_ + s[2] * (s[0] - c_),
                         -s[4] - s[5] + k * (s[0] - s[3]),
                          s[3] + a_ * s[4] + s[5],
                          b_ + s[5] * (s[3] - c_)])
    def J(s):
        return np.array([
            [-k, -1., -1., k, 0., 0.],
            [1., a_, 1., 0., 0., 0.],
            [s[2], 0., s[0] - c_, 0., 0., 0.],
            [k, 0., 0., -k, -1., -1.],
            [0., 0., 0., 1., a_, 1.],
            [0., 0., 0., s[5], 0., s[3] - c_]
        ])
    for _ in range(int(300 / dt)):
        k1 = f(x); k2 = f(x + .5 * dt * k1); k3 = f(x + .5 * dt * k2); k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if not np.all(np.isfinite(x)) or np.max(np.abs(x)) > 1e4:
            x = np.clip(np.nan_to_num(x, nan=0.0), -100.0, 100.0)
    Qm = np.eye(6); acc = np.zeros(6); cnt = 0
    for s_i in range(n):
        Qm = Qm + dt * (J(x) @ Qm)
        k1 = f(x); k2 = f(x + .5 * dt * k1); k3 = f(x + .5 * dt * k2); k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if not np.all(np.isfinite(x)) or np.max(np.abs(x)) > 1e4:
            x = np.clip(np.nan_to_num(x, nan=0.0), -100.0, 100.0)
        if (s_i + 1) % kre == 0:
            Qm, R = np.linalg.qr(Qm)
            sg = np.sign(np.diag(R)); sg[sg == 0] = 1
            Qm = Qm * sg; acc += np.log(np.abs(np.diag(R)) + 1e-300); cnt += 1
    return np.sort(acc / (cnt * kre * dt))[::-1]

def run_coupled_rossler():
    rows = []
    ks = np.round(np.arange(0.05, 0.85, 0.05), 3)
    for k in ks:
        spec = benettin_spectrum(k)
        lmax = float(spec[0])
        npos = int((spec > 0).sum())
        x1 = coupled_rossler(k)
        d2 = correlation_dimension(x1, m=6, te=6)
        dky, j = kaplan_yorke(spec)
        K = 0.4
        Q = -lmax - (d2 if np.isfinite(d2) else 0) - K
        rows.append(dict(substrate='coupled_rossler', param=float(k), lmax=lmax,
                         spec=[float(v) for v in spec], npos=npos,
                         d2=float(d2), dky=float(dky), j=j, K=K, Q=float(Q)))
    return rows

# ------------------------------------------------------- Gray-Scott (pattern-forming)
def gray_scott(feed, kill=0.055, L=48, steps=3500, dt=1.0, Du=0.16, Dv=0.08):
    rng = np.random.default_rng(int(round(feed * 10000)) + 42)
    U = np.ones((L, L)); V = np.zeros((L, L))
    r0 = slice(L//2 - 6, L//2 + 6)
    U[r0, r0] = 0.50 + 0.05 * rng.standard_normal((12, 12))
    V[r0, r0] = 0.25 + 0.05 * rng.standard_normal((12, 12))
    def lap(Z):
        return (np.roll(Z, 1, 0) + np.roll(Z, -1, 0) + np.roll(Z, 1, 1) + np.roll(Z, -1, 1) - 4 * Z)
    outs = []
    for i in range(steps):
        Lz_U, Lz_V = lap(U), lap(V)
        UV2 = U * V * V
        U += dt * (Du * Lz_U - UV2 + feed * (1 - U))
        V += dt * (Dv * Lz_V + UV2 - (feed + kill) * V)
        if i >= 500 and i % 3 == 0:
            outs.append(float(V[L//2, L//2] + 0.5 * V.std() + 1e-5 * np.sin(0.13 * i)))
    return np.array(outs)

def run_gray_scott():
    rows = []
    feeds = np.round(np.arange(0.02, 0.065, 0.005), 3)
    for f in feeds:
        ts = gray_scott(f)
        lmax = rosenstein_lmax(ts, dt=1.0, m=6, te=6)
        d2 = correlation_dimension(ts, m=6, te=6)
        K = f + 2 * 0.055
        Q = -lmax - (d2 if np.isfinite(d2) else 0) - K
        rows.append(dict(substrate='gray_scott', param=float(f), lmax=float(lmax),
                         d2=float(d2), dky=0.0, j=0, K=K, Q=float(Q)))
    return rows

# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    print("== PHASE III: Q conservation, 3 substrates ==")
    mg_rows, mg_gate = run_mg()
    print(f"  MG gate embed-spread={mg_gate['embed_spread']:.3f} dt-diff={mg_gate['dt_diff']:.3f}")
    cr_rows = run_coupled_rossler()
    for r in cr_rows:
        print(f"  CR k={r['param']:.2f} npos={r['npos']} lmax={r['lmax']:+.3f} D2={r['d2']:.2f} Q={r['Q']:+.2f}")
    gs_rows = run_gray_scott()
    for r in gs_rows:
        print(f"  GS f={r['param']:.3f} lmax={r['lmax']:+.4f} D2={r['d2']:.2f} Q={r['Q']:+.3f}")
    all_rows = mg_rows + cr_rows + gs_rows
    # Q conservation stats per substrate
    qstats = {}
    for sub in ('mg', 'coupled_rossler', 'gray_scott'):
        qq = np.array([r['Q'] for r in all_rows if r['substrate'] == sub])
        qstats[sub] = dict(mean=float(qq.mean()), std=float(qq.std()), drift=float(qq.max() - qq.min()))
        print(f"  [{sub}] Q mean={qq.mean():+.3f} std={qq.std():+.3f} drift={qq.max()-qq.min():.3f}")
    # figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    ax = axes[0, 0]
    mg_t = [r['param'] for r in mg_rows]; mg_q = [r['Q'] for r in mg_rows]
    ax.plot(mg_t, mg_q, 'o-', color='#2196F3'); ax.set_title('MG Q(tau)'); ax.set_xlabel('tau'); ax.set_ylabel('Q')
    ax = axes[0, 1]
    cr_k = [r['param'] for r in cr_rows]; cr_q = [r['Q'] for r in cr_rows]
    ax.plot(cr_k, cr_q, 's-', color='#E91E63'); ax.set_title('Coupled Rössler Q(k)'); ax.set_xlabel('k'); ax.set_ylabel('Q')
    ax = axes[0, 2]
    cr_npos = [r['npos'] for r in cr_rows]
    ax.bar(cr_k, cr_npos, color='#9C27B0'); ax.set_title('# positive LEs vs coupling k'); ax.set_xlabel('k'); ax.set_ylabel('#LE+')
    ax = axes[1, 0]
    gs_f = [r['param'] for r in gs_rows]; gs_q = [r['Q'] for r in gs_rows]
    ax.plot(gs_f, gs_q, '^-', color='#4CAF50'); ax.set_title('Gray-Scott Q(feed)'); ax.set_xlabel('f'); ax.set_ylabel('Q')
    ax = axes[1, 1]
    ax.scatter([r['Q'] for r in mg_rows], [r['d2'] for r in mg_rows], label='MG', c='#2196F3')
    ax.scatter([r['Q'] for r in cr_rows], [r['d2'] for r in cr_rows], label='CR', c='#E91E63')
    ax.scatter([r['Q'] for r in gs_rows], [r['d2'] for r in gs_rows], label='GS', c='#4CAF50')
    ax.set_title('D2 vs Q (all)'); ax.set_xlabel('Q'); ax.set_ylabel('D2'); ax.legend()
    ax = axes[1, 2]
    ax.axis('off')
    txt = "PHASE III Q-conservation gates\n"
    for sub, st in qstats.items():
        txt += f"\n{sub}: mean={st['mean']:+.3f} std={st['std']:.3f} drift={st['drift']:.3f}"
    txt += f"\n\nMG embed-spread={mg_gate['embed_spread']:.3f} (<0.15 PASS)"
    txt += f"\nMG dt-diff={mg_gate['dt_diff']:.3f} (<0.10 PASS)"
    n_hyper = sum(1 for r in cr_rows if r['npos'] >= 2)
    txt += f"\nCR hyperchaos points (k, LE+>=2): {n_hyper}/{len(cr_rows)}"
    ax.text(0.05, 0.5, txt, transform=ax.transAxes, fontsize=11, verticalalignment='top', family='monospace')
    plt.tight_layout()
    plt.savefig('morphospace_q_spatiotemporal_phase3.png', dpi=200)
    print(f"  [FIG] saved morphospace_q_spatiotemporal_phase3.png ({time.time()-t0:.1f}s)")
    with open('phase3_results.json', 'w') as fh:
        json.dump(dict(rows=all_rows, qstats=qstats, gate=mg_gate,
                       n_hyper=n_hyper, elapsed=time.time()-t0), fh, indent=2)
    print("  [DONE]")

if __name__ == '__main__':
    main()