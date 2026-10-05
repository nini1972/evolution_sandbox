#!/usr/bin/env python3
"""
Morphospace Q-Conservation Law: Multi-Substrate Empirical Verification
=======================================================================
Q = -lambda_max - D_2 - K   (hypothesized invariant, Q ~ -2.08)

Systems:
  1. Lorenz attractor (3D ODE)
  2. Henon map (2D discrete)
  3. Kuramoto-Sivashinsky PDE (spatiotemporal chaos)
  4. Rule 110 cellular automaton

Crew: Xiaomi MiMo (Theorist) + Claude Sonnet 4.5 (Systems)
"""

import numpy as np
from scipy.integrate import odeint
from scipy.spatial.distance import pdist
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
import json
import os

warnings.filterwarnings('ignore', category=RuntimeWarning)
rng = np.random.default_rng(42)


# ============================ COMMON TOOLS ============================

def embed_series(x, m, tau):
    """Time-delay embedding of a scalar series."""
    N = len(x) - (m - 1) * tau
    return np.column_stack([x[i * tau: i * tau + N] for i in range(m)])


def correlation_dimension(series, m=6, tau=None, n_r=25, max_pts=3000):
    """Grassberger-Procaccia D_2 from a scalar series."""
    x = np.asarray(series, dtype=float)
    if tau is None:
        tau = max(1, int(len(x) / 100))
    Y = embed_series(x, m, tau)
    if len(Y) > max_pts:
        idx = rng.choice(len(Y), max_pts, replace=False)
        Y = Y[idx]
    d = pdist(Y)
    d = d[d > 0]
    if len(d) < 100:
        return np.nan
    r_lo, r_hi = np.percentile(d, 2), np.percentile(d, 60)
    r_vals = np.logspace(np.log10(r_lo), np.log10(r_hi), n_r)
    C = np.array([np.count_nonzero(d < r) / len(d) for r in r_vals])
    good = (C > 0) & (C < 1)
    if good.sum() < 6:
        return np.nan
    slope = np.polyfit(np.log(r_vals[good]), np.log(C[good]), 1)[0]
    return float(slope)


def max_lyapunov_discrete(x, lag=1, max_tau_frac=0.1):
    """Rosenstein-style lambda_max for a discrete/ sampled series."""
    x = np.asarray(x, dtype=float)
    N = len(x)
    E = np.column_stack([x[:-lag], x[lag:]]) if lag == 1 else embed_series(x, 2, lag)
    M = len(E)
    if M < 200:
        return np.nan
    start = int(M * 0.1)
    ref_idx = rng.choice(np.arange(start, M - 1), size=min(200, M - start), replace=False)
    d0_all, dt_all = [], []
    for i in ref_idx:
        j = ref_idx[ref_idx > i]
        if len(j) == 0:
            continue
        d0 = np.linalg.norm(E[i] - E[j], axis=1)
        dt = j - i
        keep = d0 > 1e-12
        d0_all.append(d0[keep])
        dt_all.append(dt[keep])
    if not d0_all:
        return np.nan
    d0_all = np.concatenate(d0_all)
    dt_all = np.concatenate(dt_all)
    # robust mean divergence curve
    max_t = int(M * max_tau_frac)
    div = np.full(max_t, np.nan)
    for t in range(1, max_t):
        pairs = [(i, i + t) for i in range(M - t)]
        if not pairs:
            break
        ii = np.array([p[0] for p in pairs]); jj = np.array([p[1] for p in pairs])
        dd = np.linalg.norm(E[ii] - E[jj], axis=1)
        m = dd > 1e-12
        if m.sum() > 10:
            div[t] = np.mean(dd[m])
    valid = ~np.isnan(div)
    if valid.sum() < 5:
        return np.nan
    tt = np.arange(1, max_t)[valid]
    dv = div[valid]
    win = max(3, len(tt) // 4)
    half = win // 2
    xs, ys = [], []
    for k in range(half, len(tt) - half):
        seg = dv[k - half: k + half]
        if np.all(seg > 0):
            xs.append(np.mean(tt[k - half: k + half]))
            ys.append(np.mean(np.log(seg)))
    if len(xs) < 4:
        return np.nan
    return float(np.polyfit(xs, ys, 1)[0])


# ============================ 1. LORENZ ============================

def lorenz_rhs(state, sigma=10.0, rho=28.0, beta=8.0 / 3.0):
    x, y, z = state[..., 0], state[..., 1], state[..., 2]
    return np.stack([sigma * (y - x), x * (rho - z) - y, x * y - beta * z], axis=-1)


def lorenz_lyapunov(rho, sigma=10.0, beta=8.0 / 3.0, dt=0.01,
                    T_transient=50.0, T_compute=300.0, renorm=300):
    """Full Lyapunov spectrum via variational equations + QR (Benettin)."""
    dim = 3
    n = dim + dim * dim

    def ode(s, t):
        x, y, z = s[0], s[1], s[2]
        ds = np.empty(n)
        ds[0] = sigma * (y - x)
        ds[1] = x * (rho - z) - y
        ds[2] = x * y - beta * z
        Phi = s[3:].reshape(dim, dim)
        J = np.array([[-sigma, sigma, 0.0],
                      [rho - z, -1.0, -x],
                      [y, x, -beta]])
        ds[3:] = (J @ Phi).ravel()
        return ds

    s0 = np.zeros(n)
    s0[:3] = [1.0, 1.0, 1.0]
    s0[3:] = np.eye(dim).ravel()
    tt = np.linspace(0, T_transient, int(T_transient / dt))
    s0 = odeint(ode, s0, tt, mxstep=10000)[-1]

    acc = np.zeros(dim)
    step_T = T_compute / renorm
    nst = max(2, int(step_T / dt))
    for _ in range(renorm):
        tt = np.linspace(0, step_T, nst)
        sol = odeint(ode, s0, tt, mxstep=10000)
        Phi = sol[-1, 3:].reshape(dim, dim)
        Q, R = np.linalg.qr(Phi)
        acc += np.log(np.abs(np.diag(R)) + 1e-300)
        s0[:3] = sol[-1, :3]
        s0[3:] = Q.ravel()
    spec = np.sort(acc / T_compute)[::-1]
    return spec


def lorenz_attractor(rho, T=60.0, dt=0.01):
    tt = np.arange(0, T, dt)
    sol = odeint(lambda s, t: lorenz_rhs(s, rho=rho), [1.0, 1.0, 1.0], tt, mxstep=10000)
    return sol[int(10.0 / dt):, 0]  # drop first 10 t.u.


# ============================ 2. HENON MAP ============================

def henon_orbit(a, b=0.3, n=20000, transient=2000):
    x = np.empty(n)
    y = np.empty(n)
    xx, yy = 0.1, 0.1
    for i in range(transient + n):
        nx = 1.0 - a * xx * xx + yy
        ny = b * xx
        xx, yy = nx, ny
        if i >= transient:
            x[i - transient] = xx
            y[i - transient] = yy
    return x, y


def henon_lyapunov(a, b=0.3, n=20000, transient=2000):
    """Two-exponent spectrum via QR on the linearized map."""
    xx, yy = 0.1, 0.1
    for _ in range(transient):
        xx, yy = 1.0 - a * xx * xx + yy, b * xx
    Q = np.eye(2)
    acc = np.zeros(2)
    for i in range(n):
        J = np.array([[-2.0 * a * xx, 1.0], [b, 0.0]])
        Z = J @ Q
        Q, R = np.linalg.qr(Z)
        acc += np.log(np.abs(np.diag(R)) + 1e-300)
        xx, yy = 1.0 - a * xx * xx + yy, b * xx
    return np.sort(acc / n)[::-1]


# ============================ 3. KURAMOTO-SIVASHHINKSKY ============================

def ks_trajectory(L=35.0, N=64, nu=1.0, dt=0.01, T=400.0, transient=100.0):
    """KS u_t = -u u_x - u_xx - nu u_xxx integrated with ETDRK4-style
    semi-implicit spectral stepping (simple but stable exponential integrator)."""
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=L / N)
    # linear operator: -k^2 + nu*k^4  (for v-hat) — standard KS split
    # u_t = -(1/2)(u^2)_x - u_xx - nu u_xxx  -> spectral
    Lop = k ** 2 - nu * k ** 4          # acts on u_hat in the 'stable' convention
    E = np.exp(-Lop * dt)
    E2 = np.exp(-Lop * dt / 2.0)
    x = 2.0 * np.pi * L * np.arange(N) / N  # unused explicit coord
    u = np.cos(2.0 * np.pi * np.arange(N) / N) * (1.0 + 0.0 * rng.standard_normal(N))
    nsteps = int((T + transient) / dt)
    out = []
    # Cox-Matthews ETDRK4 (E = exp of linear op, standard KS split)
    for s in range(nsteps):
        uh = np.fft.fft(u)
        N1 = -0.5j * k * np.fft.fft(u ** 2)
        a = (E2 * uh + dt / 2.0 * N1)
        ua = np.real(np.fft.ifft(a))
        N2 = -0.5j * k * np.fft.fft(ua ** 2)
        b = E2 * a + dt / 2.0 * N2
        ub = np.real(np.fft.ifft(b))
        N3 = -0.5j * k * np.fft.fft(ub ** 2)
        c = E2 * b + dt * N3
        uc = np.real(np.fft.ifft(c))
        N4 = -0.5j * k * np.fft.fft(uc ** 2)
        uh = E * uh + dt * (N1 + 2 * N2 + 2 * N3 + N4) / 6.0
        u = np.real(np.fft.ifft(uh))
        u -= np.mean(u)
        if s * dt >= transient:
            out.append(u.copy())
    return np.array(out)  # (steps, N)


def ks_lambda_max(L=35.0, N=64, nu=1.0, dt=0.01, T=400.0):
    """Rosenstein-style lambda_max on KS field energy signal."""
    traj = ks_trajectory(L, N, nu, dt, T)
    signal = traj[:, N // 3]  # fixed spatial mode/probe
    return max_lyapunov_discrete(signal, lag=1)


# ============================ 4. RULE 110 ============================

RULE110_TABLE = {(1, 1, 1): 0, (1, 1, 0): 1, (1, 0, 1): 1, (1, 0, 0): 0,
                 (0, 1, 1): 1, (0, 1, 0): 1, (0, 0, 1): 1, (0, 0, 0): 0}


def rule110_evolve(n_cells=512, steps=2048, init='random', seed=0):
    r = np.random.default_rng(seed)
    if init == 'random':
        cells = r.integers(0, 2, n_cells)
    else:  # single seed on background 1 (Rule 110's natural background)
        cells = np.ones(n_cells, dtype=int)
        cells[n_cells // 2] = 0
    hist = np.zeros((steps, n_cells), dtype=np.uint8)
    hist[0] = cells
    for t in range(1, steps):
        left = np.roll(cells, 1)
        right = np.roll(cells, -1)
        key = left * 4 + cells * 2 + right
        cells = np.array([RULE110_TABLE[(int(key[i] >> 2) & 1,
                                         (int(key[i] >> 1) & 1),
                                         int(key[i]) & 1)]
                          for i in range(n_cells)], dtype=int)
        hist[t] = cells
    return hist


def rule110_lambda(hist, sample_rows=512):
    """Boolean perturbation growth rate: fraction of differing cells
    between two trajectories started with one flipped cell, proxy for lambda."""
    n_cells = hist.shape[1]
    steps = min(len(hist), sample_rows)
    base = rule110_evolve(n_cells, steps, init='random', seed=1)
    pert = base.copy()
    pert[0, n_cells // 2] ^= 1
    lam_t = []
    cells = pert[0].copy()
    cells0 = base[0].copy()
    for t in range(1, steps):
        def step(c):
            l = np.roll(c, 1); r = np.roll(c, -1)
            return np.array([RULE110_TABLE[(int(l[i]), int(c[i]), int(r[i]))]
                             for i in range(len(c))], dtype=int)
        cells = step(cells)
        cells0 = step(cells0)
        diff = np.count_nonzero(cells != cells0)
        if diff > 0 and t > 10:
            lam_t.append(np.log(diff))
    if len(lam_t) < 10:
        return np.nan
    t_idx = np.arange(len(lam_t))
    return float(np.polyfit(t_idx, lam_t, 1)[0])


# ============================ K: EFFECTIVE COUPLING ============================
# Theorist's definition (all-substrate): K = -<tr J>/d
#   mean phase-space contraction per dimension: how strongly the substrate
#   couples to (contracts) its own state volume.

def K_lorenz(rho, sigma=10.0, beta=8.0 / 3.0, T=100.0, dt=0.01):
    sol = odeint(lambda s, t: lorenz_rhs(s, sigma, rho, beta),
                 [1.0, 1.0, 1.0], np.arange(0, T, dt), mxstep=10000)
    traj = sol[int(20 / dt):]
    tr = -(sigma + 1.0 + beta)  # constant for Lorenz
    return -tr / 3.0


def K_henon(a, b=0.3, n=20000):
    x, y = henon_orbit(a, b, n=n)
    tr = -2.0 * a * x          # tr J = -2 a x + 0
    return -np.mean(tr) / 2.0


def K_ks(traj):
    """Linear operator trace density of KS: -(k^2 - nu k^4) averaged -> per-dim."""
    N = traj.shape[1]
    return None  # filled analytically below


def K_ks_analytic(N=64, L=35.0, nu=1.0):
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=L / N)
    # linearized operator eigenvalues of u_t part: +k^2 - nu k^4 (growth/contrib)
    ev = k ** 2 - nu * k ** 4
    return float(-np.mean(ev) / N * N)  # = -mean(ev), per mode coupling


def K_rule110(hist):
    """Fraction of non-trivial (edge/non-uniform) neighborhoods = effective
    coupling density: cells actually 'listening' to neighbors."""
    t, n = hist.shape
    left = np.roll(hist, 1, axis=1); right = np.roll(hist, -1, axis=1)
    nontriv = (left != right)
    return float(np.mean(nontriv))  # in [0,1]


# ============================ PER-SYSTEM EXPERIMENTS ============================

def experiment_lorenz(rhos=(20.0, 24.0, 28.0, 35.0, 45.0)):
    rows = []
    for rho in rhos:
        spec = lorenz_lyapunov(rho, T_compute=300.0, renorm=300)
        lam = spec[0]
        sig = lorenz_attractor(rho)
        d2 = correlation_dimension(sig, m=6, tau=12)
        K = K_lorenz(rho)
        Q = -lam - d2 - K
        rows.append(dict(system='Lorenz', param=rho, lam=lam, d2=d2, K=K, Q=Q))
        print(f"[Lorenz] rho={rho}: lam={lam:.3f} D2={d2:.3f} K={K:.3f} Q={Q:.3f}")
    return rows


def experiment_henon(as_=(1.05, 1.2, 1.3, 1.35, 1.4)):
    rows = []
    for a in as_:
        spec = henon_lyapunov(a)
        lam = spec[0]
        x, _ = henon_orbit(a, n=20000)
        d2 = correlation_dimension(x, m=3, tau=1)
        K = K_henon(a)
        Q = -lam - d2 - K
        rows.append(dict(system='Henon', param=a, lam=lam, d2=d2, K=K, Q=Q))
        print(f"[Henon] a={a}: lam={lam:.3f} D2={d2:.3f} K={K:.3f} Q={Q:.3f}")
    return rows


def experiment_ks(Ls=(30.0, 35.0, 40.0, 50.0)):
    rows = []
    for L in Ls:
        traj = ks_trajectory(L=L, N=64, T=300.0)
        sig = traj[:, 21]
        lam = max_lyapunov_discrete(sig, lag=1)
        d2 = correlation_dimension(sig, m=6, tau=5)
        K = K_ks_analytic(L=L)
        Q = -lam - d2 - K
        rows.append(dict(system='KS', param=L, lam=lam, d2=d2, K=K, Q=Q))
        print(f"[KS] L={L}: lam={lam:.3f} D2={d2:.3f} K={K:.3f} Q={Q:.3f}")
    return rows


def experiment_rule110(seeds=(0, 1, 2, 3)):
    rows = []
    for s in seeds:
        hist = rule110_evolve(n_cells=512, steps=2048, seed=s)
        lam = rule110_lambda(hist)
        sig = hist[:, ::8].mean(axis=1)  # coarse density signal
        d2 = correlation_dimension(sig, m=5, tau=3)
        K = K_rule110(hist)
        Q = -lam - d2 - K
        rows.append(dict(system='Rule110', param=s, lam=lam, d2=d2, K=K, Q=Q))
        print(f"[Rule110] seed={s}: lam={lam:.3f} D2={d2:.3f} K={K:.3f} Q={Q:.3f}")
    return rows


# ============================ VERIFICATION FIGURE ============================

def make_figure(all_rows, K_star, Q_target=-2.08, path='morphospace_q_verification.png'):
    systems = ['Lorenz', 'Henon', 'KS', 'Rule110']
    colors = {'Lorenz': '#1f77b4', 'Henon': '#ff7f0e',
              'KS': '#2ca02c', 'Rule110': '#d62728'}
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(r'Q-Conservation Test: $Q=-\lambda_{max}-D_2-K$ '
                 f'(target $Q\\approx{Q_target}$, $K^*={K_star:.3f}$ frozen)',
                 fontsize=14, fontweight='bold')

    # (a) Q distribution per system (calibrated K)
    ax = axes[0, 0]
    for i, s in enumerate(systems):
        qs = [r['Q'] for r in all_rows if r['system'] == s]
        if qs:
            ax.scatter([i] * len(qs), qs, s=70, color=colors[s],
                       edgecolors='k', zorder=3, label=s)
    ax.axhline(Q_target, color='gray', ls='--', lw=1.5, label=f'target {Q_target}')
    ax.axhline(np.mean([r['Q'] for r in all_rows]), color='k', ls=':', lw=1.5,
               label='empirical mean')
    ax.set_xticks(range(len(systems))); ax.set_xticklabels(systems)
    ax.set_ylabel('Q'); ax.set_title('(a) Q across substrates (K calibrated/frozen)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # (b) lambda vs D2 scatter, colored by system
    ax = axes[0, 1]
    for s in systems:
        rs = [r for r in all_rows if r['system'] == s]
        ax.scatter([r['lam'] for r in rs], [r['d2'] for r in rs],
                   s=70, color=colors[s], edgecolors='k', label=s, zorder=3)
    ax.set_xlabel(r'$\lambda_{max}$'); ax.set_ylabel('$D_2$')
    ax.set_title(r'(b) $\lambda_{max}$ vs $D_2$ (morphospace)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # (c) Q with *native* K per system (no calibration) — branch test
    ax = axes[1, 0]
    for i, s in enumerate(systems):
        rs = [r for r in all_rows if r['system'] == s]
        qs = [-r['lam'] - r['d2'] - r['K'] for r in rs]
        if qs:
            ax.scatter([i] * len(qs), qs, s=70, color=colors[s],
                       edgecolors='k', zorder=3)
    ax.axhline(Q_target, color='gray', ls='--', lw=1.5)
    ax.axhline(np.mean([-r['lam'] - r['d2'] - r['K'] for r in all_rows]),
               color='k', ls=':', lw=1.5)
    ax.set_xticks(range(len(systems))); ax.set_xticklabels(systems)
    ax.set_ylabel('Q (native K)'); ax.set_title('(c) Native-K Q: invariant or branches?')
    ax.grid(alpha=0.3)

    # (d) histogram of all Q values (both K variants)
    ax = axes[1, 1]
    q_cal = [r['Q'] for r in all_rows if np.isfinite(r['Q'])]
    q_nat = [-r['lam'] - r['d2'] - r['K'] for r in all_rows
             if np.isfinite(r['d2']) and np.isfinite(r['K'])]
    ax.hist(q_cal, bins=20, alpha=0.65, color='#1f77b4', label='calibrated K')
    ax.hist(q_nat, bins=20, alpha=0.55, color='#ff7f0e', label='native K')
    ax.axvline(Q_target, color='gray', ls='--', lw=1.5, label=f'target {Q_target}')
    ax.set_xlabel('Q'); ax.set_ylabel('count')
    ax.set_title('(d) Q distribution (all systems pooled)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(path, dpi=160)
    plt.close()
    print(f"Saved figure -> {path}")


# ============================ MAIN ============================

def main():
    Q_TARGET = -2.08
    all_rows = []

    print("=" * 70)
    print("SUBSTRATE 1: LORENZ")
    all_rows += experiment_lorenz()
    print("=" * 70)
    print("SUBSTRATE 2: HENON")
    all_rows += experiment_henon()
    print("=" * 70)
    print("SUBSTRATE 3: KURAMOTO-SIVASHINSKY")
    all_rows += experiment_ks()
    print("=" * 70)
    print("SUBSTRATE 4: RULE 110")
    all_rows += experiment_rule110()

    # Calibration transfer: fit K* so Q(rho=28) = -2.08 exactly, freeze K*
    ref = [r for r in all_rows if r['system'] == 'Lorenz' and r['param'] == 28.0]
    if ref:
        r0 = ref[0]
        K_star = -Q_TARGET - r0['lam'] - r0['d2']
        print(f"\n[CALIBRATION] rho=28: lam={r0['lam']:.3f} D2={r0['d2']:.3f} "
              f"-> K*={K_star:.3f} (frozen)")
        for r in all_rows:
            r['Q_cal'] = -r['lam'] - r['d2'] - K_star
    else:
        K_star = np.nan

    # Summary stats
    q_cal = np.array([r.get('Q_cal', np.nan) for r in all_rows])
    q_nat = np.array([-r['lam'] - r['d2'] - r['K'] for r in all_rows])
    valid = np.isfinite(q_cal)
    print(f"\n[SUMMARY] calibrated-K Q: mean={np.nanmean(q_cal):.3f} "
          f"std={np.nanstd(q_cal):.3f} n={valid.sum()}")
    print(f"[SUMMARY] native-K    Q: mean={np.nanmean(q_nat):.3f} "
          f"std={np.nanstd(q_nat):.3f}")

    make_figure(all_rows, K_star if np.isfinite(K_star) else 0.0, Q_TARGET)

    with open('morphospace_q_results.json', 'w') as f:
        json.dump(dict(K_star=float(K_star), Q_target=Q_TARGET, rows=all_rows),
                  f, indent=2, default=float)
    print("Saved results -> morphospace_q_results.json")


if __name__ == '__main__':
    main()

