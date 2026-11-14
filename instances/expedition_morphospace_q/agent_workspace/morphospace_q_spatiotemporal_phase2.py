#!/usr/bin/env python3
"""
Morphospace Q — Phase II: Spatiotemporal & Delay-Differential Q-Branches
=========================================================================
Extends Phase I (morphospace_q_conservation.py, 4-substrate BIFURCATED verdict,
invariance ratio 9.655) to three new substrates:

  (a) Mackey-Glass delay DDE   : continuous tau-sweep 17..30 across the
                                 period-doubling route to chaos -> Q(tau)
  (b) Gray-Scott reaction-diffusion : feed-rate sweep (mitosis -> solitons)
  (c) Rossler 4D hyperchaos    : full exact QR Lyapunov spectrum, gate: 2 pos LEs

Metrics per parameter point: lambda_max, full Lyapunov spectrum,
Kaplan-Yorke dimension D_KY, correlation dimension D_2, Q = -lmax - D2 - K.

Hypotheses (per phase2_theory_answers.md):
  H1 intra-substrate Q-conservation (bounded Q(theta) within a sweep)
  H2 cross-substrate branching persists -> 7 distinct branches total
  H3 Q(tau) bounded across MG cascade iff D2 compensates lambda_max
     Falsifier: systematic drift > 2.4 (2x Phase I Lorenz branch std)

Hard gates:
  G1 MG:  lambda_max(tau=23) in [0.025, 0.045]  (literature ~0.034)
  G2 MG:  embedding convergence: lmax stable +/-5% over m x tau_emb grid
  G3 Rossler: j = max{k: sum l_i > 0} >= 2  (true hyperchaos)

Headless. Outputs:
  morphospace_q_spatiotemporal_phase2.png   (multi-panel figure)
  morphospace_q_spatiotemporal_phase2.json  (all metrics)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, json, os, sys, time

OUT_JSON = 'morphospace_q_spatiotemporal_phase2.json'
OUT_PNG  = 'morphospace_q_spatiotemporal_phase2.png'
RNG = np.random.default_rng(20261109)

# ---------------------------------------------------------------- utilities
def numerical_jacobian(f, x, rel=1e-6):
    n = x.size
    J = np.zeros((n, n))
    fx = f(x)
    for i in range(n):
        h = rel * max(1.0, abs(x[i]))
        xp = x.copy(); xp[i] += h
        J[:, i] = (f(xp) - fx) / h
    return J


def rk4_step(f, x, dt):
    k1 = f(x)
    k2 = f(x + 0.5 * dt * k1)
    k3 = f(x + 0.5 * dt * k2)
    k4 = f(x + dt * k3)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def benettin_spectrum(f, x0, n_dim, n_steps, dt, k_reorth, n_exp, t_burn=0.0):
    """Exact QR Lyapunov spectrum of an autonomous ODE flow via tangent map."""
    n_dim = int(n_dim)
    x = np.array(x0, float).copy()
    if t_burn > 0:
        for _ in range(int(t_burn / dt)):
            x = rk4_step(f, x, dt)
    Q = np.eye(n_dim)
    acc = np.zeros(n_dim)
    cnt = 0
    for step in range(n_steps):
        J = numerical_jacobian(f, x)
        Q = Q + dt * (J @ Q)          # variational eq, Euler-Cauchy
        x = rk4_step(f, x, dt)
        if (step + 1) % k_reorth == 0:
            Q, R = np.linalg.qr(Q)
            s = np.sign(np.diag(R)); s[s == 0] = 1.0
            Q = Q * s
            acc += np.log(np.abs(np.diag(R)) + 1e-300)
            cnt += 1
    spec = np.sort(acc / (cnt * k_reorth * dt))[::-1]
    return spec[:n_exp] if n_exp <= n_dim else spec


def kaplan_yorke(lams):
    """lams sorted descending. j = max{k: sum_{i<=k} l_i > 0}."""
    lams = np.asarray(lams, float)
    c = np.cumsum(lams)
    pos = np.where(c > 0)[0]
    if pos.size == 0:
        return 0.0, 0
    j = int(pos[-1]) + 1
    if j >= lams.size:
        return float(lams.size), int(lams.size)
    return float(j + c[j - 1] / abs(lams[j])), j


# ------------------------------------------------- embedding / delay tools
def takens_embed(series, m, tau_emb):
    n = len(series) - (m - 1) * tau_emb
    E = np.empty((n, m))
    for i in range(m):
        E[:, i] = series[i * tau_emb: i * tau_emb + n]
    return E


def embedding_lyapunov(series, m, tau_emb, dt_eff, n_exp=3, k_reorth=10,
                       n_steps=None):
    """Benettin on delay-embedded point map (global linear map fit)."""
    E = takens_embed(series, m, tau_emb)
    dim = E.shape[1]
    if n_steps is None:
        n_steps = E.shape[0] - 1
    n_steps = min(n_steps, E.shape[0] - 2)
    step_time = dt_eff * tau_emb
    X = E[:n_steps]; Y = E[1:n_steps + 1]
    A = np.linalg.lstsq(np.hstack([X, np.ones((X.shape[0], 1))]), Y, rcond=None)[0]
    Amat = A[:dim].T
    Q = np.eye(dim)
    acc = np.zeros(dim); cnt = 0
    for step in range(n_steps):
        Q = Amat @ Q
        if (step + 1) % k_reorth == 0:
            Q, R = np.linalg.qr(Q)
            s = np.sign(np.diag(R)); s[s == 0] = 1.0
            Q = Q * s
            acc += np.log(np.abs(np.diag(R)) + 1e-300)
            cnt += 1
    if cnt == 0:
        return np.zeros(dim)
    return np.sort(acc / (cnt * step_time))[::-1]


def correlation_dimension(series, emb_m=6, emb_tau=6, theiler=50):
    """Grassberger-Procaccia plateau estimator (Phase I validated)."""
    E = takens_embed(series, emb_m, emb_tau)
    N = E.shape[0]
    if N > 1600:
        sel = np.sort(RNG.choice(N, 1600, replace=False)); E = E[sel]; N = 1600
    D = np.sqrt(((E[:, None, :] - E[None, :, :]) ** 2).sum(-1))
    iu = np.triu_indices(N, 1)
    d = D[iu]
    mask = np.abs(iu[0] - iu[1]) > theiler
    d = d[mask]; d = d[d > 0]
    if d.size < 100:
        return float('nan')
    rs = np.exp(np.linspace(np.log(np.percentile(d, 5)),
                            np.log(np.percentile(d, 95)), 40))
    Nc = np.array([np.mean(d < r) for r in rs])
    good = (Nc > 0) & (Nc < 1)
    if good.sum() < 8:
        return float('nan')
    slope = np.gradient(np.log(Nc[good]), np.log(rs[good]))
    w = (slope > 0.2) & (slope < 6)
    if w.sum() < 4:
        w = np.ones_like(slope, bool)
    return float(np.median(slope[w]))


def rosenstein_lmax(series, dt, emb_m=6, emb_tau=6, max_steps=500):
    """Largest LE from divergence of nearest neighbors (Rosenstein)."""
    E = takens_embed(series, emb_m, emb_tau)
    N = E.shape[0]
    if N > 2500:
        sel = np.sort(RNG.choice(N, 2500, replace=False)); E = E[sel]; N = 2500
    Dm = np.sqrt(((E[:, None, :] - E[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(Dm, np.inf)
    theiler = emb_m * emb_tau
    for i in range(N):
        lo = max(0, i - theiler); hi = min(N, i + theiler + 1)
        Dm[i, lo:hi] = np.inf
    nn = np.argmin(Dm, axis=1)
    d0 = Dm[np.arange(N), nn]
    step = dt * emb_tau
    div = []
    for k in range(1, max_steps):
        j = np.arange(N - k)
        valid = d0[j] > 0
        if valid.sum() < 30: break
        dk = np.sqrt(((E[j + k] - E[nn[j] + k]) ** 2).sum(-1))
        dk = dk[valid]
        m_d = np.mean(dk)
        if m_d <= 0: continue
        div.append((k * step, m_d))
    if len(div) < 6: return float('nan')
    t_arr = np.array([d[0] for d in div]); d_arr = np.array([d[1] for d in div])
    nfit = max(6, int(0.2 * len(t_arr)))
    return float(np.polyfit(t_arr[:nfit], np.log(d_arr[:nfit]), 1)[0])


# ================================================================ (a) Mackey-Glass
MG_BETA, MG_GAMMA, MG_N = 0.2, 0.1, 10.0


def mg_series(tau, dt=0.05, T_burn=3000.0, T_sample=4000.0):
    """MG DDE integration with ring-buffer delay lookup (index-exact)."""
    n_b = int(T_burn / dt); n_s = int(T_sample / dt)
    n_tau = int(round(tau / dt))
    L = n_tau + 1
    ring = np.full(L, 0.5)
    x = 0.5
    out = np.empty(n_s)

    def deriv(xc, xd):
        return MG_BETA * xd / (1 + xd ** MG_N) - MG_GAMMA * xc

    for i in range(n_b + n_s):
        xd = ring[i % L]
        k1 = deriv(x, xd)
        k2 = deriv(x + 0.5 * dt * k1, xd)
        k3 = deriv(x + 0.5 * dt * k2, xd)
        k4 = deriv(x + dt * k3, xd)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        ring[(i + 1) % L] = x
        if i >= n_b:
            out[i - n_b] = x
    return out


def run_mackey_glass():
    taus = np.round(np.arange(17.0, 30.01, 0.5), 2)
    rows = []
    print("[MG] sweep tau = 17..30 (dt=0.05)")
    t0 = time.time()
    # gate G2: embedding convergence at tau=23
    s23 = mg_series(23.0, T_burn=3000, T_sample=4000)
    lvals = []
    for m in (6, 8, 10, 12):
        for te in (4, 6, 8, 10):
            spec = embedding_lyapunov(s23, m, te, dt_eff=0.05, n_exp=1)
            lvals.append(spec[0])
    lvals = np.array(lvals)
    rel_spread = (np.nanmax(lvals) - np.nanmin(lvals)) / max(abs(np.nanmean(lvals)), 1e-9)
    gate_g2 = rel_spread <= 0.05
    # gate G1: physics
    l23 = float(np.nanmedian(lvals))
    gate_g1 = 0.025 <= l23 <= 0.045
    print(f"  G1 physics: lmax(23)={l23:.4f} (need 0.025..0.045) -> {'PASS' if gate_g1 else 'FAIL'}")
    print(f"  G2 embed-converge: rel spread={rel_spread:.3f} -> {'PASS' if gate_g2 else 'FAIL'}")
    for tau in taus:
        s = mg_series(float(tau))
        spec = embedding_lyapunov(s, 8, 6, dt_eff=0.05, n_exp=4)
        lmax = float(spec[0])
        d2 = correlation_dimension(s, emb_m=6, emb_tau=6)
        dky, j = kaplan_yorke(spec)
        K = MG_GAMMA  # substrate-native: K = gamma = 0.1 constant
        Q = -lmax - (d2 if np.isfinite(d2) else 0.0) - K
        rows.append(dict(substrate='mackey_glass', param=float(tau), lmax=lmax,
                         spec=[float(v) for v in spec], d2=float(d2),
                         dky=float(dky), j=int(j), K=float(K), Q=float(Q)))
        print(f"  tau={tau:5.1f} lmax={lmax:+.4f} D2={d2:.3f} DKY={dky:.3f} "
              f"j={j} Q={Q:+.3f}")
    print(f"  [MG] done in {time.time()-t0:.1f}s")
    return rows, dict(gate_g1=bool(gate_g1), gate_g2=bool(gate_g2),
                      lmax_tau23=l23)


# ================================================================ (c) Rossler 4D hyperchaos
def rossler4(x, a=0.25, b=3.0, c=0.5, d=0.05):
    dx = -x[1] - x[2] + a * x[0]
    dy = x[0] + a * x[1] + x[3]
    dz = b + x[0] * x[2]
    dw = -c * x[2] + d * x[3]
    return np.array([dx, dy, dz, dw])


def run_rossler(params_list):
    rows = []
    for (a, b, c, d) in params_list:
        x0 = np.array([1.0, 1.0, 1.0, 1.0])
        f = lambda x: rossler4(x, a, b, c, d)
        spec = benettin_spectrum(f, x0, n_dim=4, n_steps=60000, dt=0.01,
                                 k_reorth=10, n_exp=4, t_burn=500.0)
        x = x0.copy()
        for _ in range(int(500 / 0.01)):
            x = rk4_step(f, x, 0.01)
        ser = np.empty(4000)
        for i in range(4000):
            x = rk4_step(f, x, 0.01)
            ser[i] = x[0]
        d2 = correlation_dimension(ser, emb_m=6, emb_tau=6)
        dky, j = kaplan_yorke(spec)
        K = c  # substrate-native z-damping
        Q = -spec[0] - (d2 if np.isfinite(d2) else 0.0) - K
        rows.append(dict(substrate='rossler4', param=f"a={a},b={b},c={c},d={d}",
                         lmax=float(spec[0]), spec=[float(v) for v in spec],
                         d2=float(d2), dky=float(dky), j=int(j), K=float(K),
                         Q=float(Q)))
        print(f"  Rossler({a},{b},{c},{d}): spec={np.round(spec,4)} j={j} "
              f"D2={d2:.3f} DKY={dky:.3f} Q={Q:+.3f}")
    gate_g3 = all(r['j'] >= 2 for r in rows)
    print(f"  G3 hyperchaos (j>=2 everywhere): {'PASS' if gate_g3 else 'FAIL'}")
    return rows, dict(gate_g3=bool(gate_g3))


# ================================================================ (b) Gray-Scott
def run_gray_scott_local():
    """Lightweight local Gray-Scott feed-sweep; heavy refinement -> World C."""
    rows = []
    N = 64; L = 1.0; dx = L / N
    Du, Dv = 1.6e-3, 8.0e-4
    dt = 1.0
    f_list = np.round(np.arange(0.020, 0.0601, 0.005), 4)
    k = 0.062
    print(f"[GS] local feed-sweep f={f_list[0]}..{f_list[-1]} at k={k} (N={N})")
    for f in f_list:
        U = np.ones((N, N)); V = np.zeros((N, N))
        U[24:40, 24:40] = 0.5; V[24:40, 24:40] = 0.25
        rng = np.random.default_rng(1)
        U += 0.01 * rng.standard_normal((N, N))
        probe = np.empty(3000)

        def lap(a):
            return (np.roll(a, 1, 0) + np.roll(a, -1, 0) +
                    np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a)

        for i in range(9000):
            lU, lV = lap(U), lap(V)
            UV2 = U * V * V
            U += dt * (Du * lU - UV2 + f * (1 - U))
            V += dt * (Dv * lV + UV2 - (f + k) * V)
            if i >= 6000:
                probe[i - 6000] = V.mean()
        lmax = rosenstein_lmax(probe, dt=1.0, emb_m=6, emb_tau=6)
        d2 = correlation_dimension(probe, emb_m=6, emb_tau=6)
        K = f + 2 * k  # Jacobian-trace native dissipation
        Q = -lmax - (d2 if np.isfinite(d2) else 0.0) - K
        rows.append(dict(substrate='gray_scott', param=f"f={f},k={k}",
                         lmax=float(lmax), spec=[float(lmax)],
                         d2=float(d2), dky=float('nan'), j=0,
                         K=float(K), Q=float(Q)))
        print(f"  f={f:.3f} lmax={lmax:+.4f} D2={d2:.3f} K={K:.4f} Q={Q:+.3f}")
    return rows, {}


# ================================================================ figure
def make_figure(mg_rows, ro_rows, gs_rows, tests, phase1):
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.42, wspace=0.30)

    tau = np.array([r['param'] for r in mg_rows])
    Q = np.array([r['Q'] for r in mg_rows])
    lm = np.array([r['lmax'] for r in mg_rows])
    d2 = np.array([r['d2'] for r in mg_rows])
    dky = np.array([r['dky'] for r in mg_rows])

    # (1) Q(tau) trajectory
    ax = fig.add_subplot(gs[0, 0:2])
    ax.plot(tau, Q, 'o-', color='tab:blue', ms=4, lw=1.6, label=r'$Q(\tau)$')
    ax.axhspan(np.mean(Q) - np.std(Q), np.mean(Q) + np.std(Q),
               color='tab:blue', alpha=0.15, label='±1σ band')
    ax.axhline(np.mean(Q), ls='--', color='tab:blue', lw=1)
    ax.axhline(np.mean(Q) + 2.4, ls=':', color='crimson', lw=1.4,
               label='H3 falsifier (±2.4)')
    ax.axhline(np.mean(Q) - 2.4, ls=':', color='crimson', lw=1.4)
    ax.set_xlabel(r'$\tau$ (Mackey-Glass delay)')
    ax.set_ylabel('Q')
    ax.set_title('(a) Q(τ) across MG cascade  '
                 f"drift={tests['H1_mg_q_range']:.2f} "
                 f"{'PASS' if tests['H3_pass'] else 'FAIL'}")
    ax.legend(fontsize=8, loc='best')

    # (2) spectra vs tau
    ax = fig.add_subplot(gs[0, 2])
    ax.plot(tau, lm, 's-', color='tab:red', ms=4, label=r'$\lambda_{max}$')
    ax.plot(tau, d2, '^-', color='tab:green', ms=4, label=r'$D_2$')
    ax.plot(tau, dky, 'd-', color='tab:purple', ms=4, label=r'$D_{KY}$')
    ax.set_xlabel(r'$\tau$'); ax.set_title('(b) MG spectra vs τ')
    ax.legend(fontsize=8)

    # (3) 7-substrate branch map
    ax = fig.add_subplot(gs[1, 0:2])
    labels = list(phase1.keys()) + ['MackeyGlass', 'GrayScott', 'Rossler4']
    means = [phase1['Lorenz'], phase1['Henon'], phase1['KS'], phase1['Rule110'],
             np.nanmean(Q), np.nanmean([r['Q'] for r in gs_rows]),
             np.nanmean([r['Q'] for r in ro_rows])]
    stds = [1.178, 0.937, 0.301, 0.154,
            np.nanstd(Q), np.nanstd([r['Q'] for r in gs_rows]),
            np.nanstd([r['Q'] for r in ro_rows])]
    colors = ['tab:orange']*4 + ['tab:blue', 'tab:cyan', 'tab:purple']
    for i, (m, s, c) in enumerate(zip(means, stds, colors)):
        ax.errorbar(i, m, yerr=s, fmt='o', color=c, capsize=4, ms=7)
    ax.axhline(-2.08, ls='--', color='gray', lw=1.2,
               label=r'Phase I target $Q^*=-2.08$')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha='right')
    ax.set_ylabel('Q')
    ax.set_title(f"(c) 7-substrate branch map — {tests['verdict']}  "
                 f"min gap={tests['min_branch_gap']:.2f}")
    ax.legend(fontsize=8)

    # (4) Rossler spectra bar
    ax = fig.add_subplot(gs[1, 2])
    if ro_rows:
        sp = np.array([r['spec'] for r in ro_rows])
        x = np.arange(sp.shape[1])
        for i in range(sp.shape[0]):
            ax.bar(x + i * 0.25, sp[i], width=0.25, label=f"run{i}")
        ax.axhline(0, color='k', lw=0.8)
        ax.set_title('(d) Rössler-4D spectra (j gate)')
        ax.legend(fontsize=7)

    # (5) Gray-Scott Q(f)
    ax = fig.add_subplot(gs[2, 0])
    if gs_rows:
        f = [float(str(r['param']).split(',')[0].split('=')[1]) for r in gs_rows]
        gQ = [r['Q'] for r in gs_rows]
        ax.plot(f, gQ, 'o-', color='tab:cyan')
    ax.set_xlabel('feed f'); ax.set_ylabel('Q')
    ax.set_title('(e) Gray-Scott Q(f)')

    # (6) Q scatter all substrates
    ax = fig.add_subplot(gs[2, 1:])
    allsub = ([('Lorenz', -6.788), ('Hénon', -1.272), ('KS', -1.620),
               ('Rule110', -3.266)] +
              [(f'MG τ={t:.0f}', q) for t, q in zip(tau, Q)] +
              [('GS', r['Q']) for r in gs_rows] +
              [('Rossler', r['Q']) for r in ro_rows])
    xs = np.arange(len(allsub))
    ys = [s[1] for s in allsub]
    cs = ['tab:orange']*4 + ['tab:blue']*len(tau) + \
         ['tab:cyan']*len(gs_rows) + ['tab:purple']*len(ro_rows)
    ax.scatter(xs, ys, c=cs, s=18)
    ax.axhline(-2.08, ls='--', color='gray', lw=1)
    ax.set_title('(f) All-substrate Q scatter (Phase I + II)')
    ax.set_xlabel('index'); ax.set_ylabel('Q')

    fig.suptitle('Morphospace Q — Phase II: spatiotemporal / delay / hyperchaos',
                 fontsize=14, y=0.98)
    fig.savefig(OUT_PNG, dpi=140, bbox_inches='tight')
    plt.close(fig)


# ================================================================ main
def main():
    t0 = time.time()
    print("=" * 70)
    print("MORPHOSPACE Q — PHASE II: spatiotemporal / delay / hyperchaos branches")
    print("=" * 70)

    mg_rows, mg_gates = run_mackey_glass()
    ro_rows, ro_gates = run_rossler([
        (0.25, 3.0, 0.5, 0.05),
        (0.25, 3.0, 0.5, 0.01),
        (0.30, 3.5, 0.5, 0.01),
    ])
    gs_rows, gs_gates = run_gray_scott_local()

    all_rows = mg_rows + ro_rows + gs_rows

    mg_Q = np.array([r['Q'] for r in mg_rows])
    gs_Q = np.array([r['Q'] for r in gs_rows])
    ro_Q = np.array([r['Q'] for r in ro_rows])
    mg_drift = float(np.nanmax(mg_Q) - np.nanmin(mg_Q)) if mg_Q.size else float('nan')
    h3_pass = bool(mg_drift <= 2.4)

    branch_means = dict(mackey_glass=float(np.nanmean(mg_Q)) if mg_Q.size else float('nan'),
                        gray_scott=float(np.nanmean(gs_Q)) if gs_Q.size else float('nan'),
                        rossler4=float(np.nanmean(ro_Q)) if ro_Q.size else float('nan'))
    phase1 = dict(Lorenz=-6.788, Henon=-1.272, KS=-1.620, Rule110=-3.266)
    means = list(branch_means.values()) + list(phase1.values())
    all_std = float(np.nanstd(means))
    gaps = [abs(a - b) for i, a in enumerate(means) for b in means[i+1:]]
    min_gap = float(np.nanmin(gaps))
    verdict = ('BIFURCATED' if min_gap > 0.5 else
               ('INVARIANT' if all_std < 0.5 else 'MIXED'))

    tests = dict(H1_mg_q_range=mg_drift, H3_pass=h3_pass,
                 branch_means=phase1 | branch_means,
                 min_branch_gap=min_gap, all_branch_std=all_std,
                 verdict=verdict, gates=mg_gates | ro_gates | gs_gates)
    print("\n--- TESTS ---")
    print(json.dumps(tests, indent=2))

    json.dump(dict(rows=all_rows, tests=tests), open(OUT_JSON, 'w'), indent=2)
    print(f"[saved] {OUT_JSON}")

    make_figure(mg_rows, ro_rows, gs_rows, tests, phase1)
    print(f"[saved] {OUT_PNG}")
    print(f"TOTAL {time.time()-t0:.1f}s")


if __name__ == '__main__':
    main()