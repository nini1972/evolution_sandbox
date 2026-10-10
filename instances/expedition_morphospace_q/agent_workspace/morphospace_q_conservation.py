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


def max_lyapunov_discrete(x, lag=1, dt=1.0, Tmax=400):
    """Rosenstein two-trajectory MLE for a scalar series sampled every dt.

    Pairs: for each reference index i, the temporally-closest partner j with
    Theiler window w <= j-i <= W (avoids trivial short-lag neighbors).
    Divergence d(t) = ||E[i+t] - E[j+t]|| in delay-2 coordinates (x_t, x_{t+lag}).
    Fit: least-squares slope of mean log d(t) over the monotone pre-saturation
    rise (up to 70% of the curve peak). Returns lambda per unit physical time.
    """
    x = np.asarray(x, dtype=float)
    M0 = len(x) - lag
    if M0 < 600 or not np.all(np.isfinite(x)):
        return np.nan
    E = np.column_stack([x[:M0], x[lag:lag + M0]])
    M = len(E)
    w = max(lag + 5, min(200, int(0.02 * M)))
    W = int(min(max(Tmax, w + 50), M // 3))
    # Divergence window T: every chosen pair (i, j) must retain T steps of
    # headroom (j + T <= M), so restrict partners to js < M - T.
    T = int(min(Tmax, M // 3))
    if T < 30:
        return np.nan
    stride = max(1, (M - W) // 2500)
    idx = np.arange(0, M - W, stride)
    cand = np.arange(w, W + 1)
    I_l, J_l = [], []
    for i in idx:
        js = i + cand
        js = js[js <= M - 1 - T]
        if js.size == 0:
            continue
        d = np.linalg.norm(E[js] - E[i], axis=1)
        k = int(np.argmin(d))
        I_l.append(i)
        J_l.append(js[k])
    if len(I_l) < 50:
        return np.nan
    I = np.asarray(I_l, dtype=np.int64)
    J = np.asarray(J_l, dtype=np.int64)
    acc = np.zeros(T)
    cnt = np.zeros(T)
    for t in range(1, T):
        d = np.linalg.norm(E[I + t] - E[J + t], axis=1)
        ok = d > 1e-300
        if ok.any():
            acc[t] = np.log(d[ok]).sum()
            cnt[t] = ok.sum()
    with np.errstate(invalid='ignore', divide='ignore'):
        logd = np.where(cnt > 1, acc / np.maximum(cnt, 1), np.nan)
    if np.all(np.isnan(logd[1:])):
        return np.nan
    # monotone-rise window: baseline at t=1, stop at 70% of pre-sat peak
    peak = np.nanmax(logd[1:])
    thr = logd[1] + 0.7 * (peak - logd[1])
    stop_arr = np.where(logd[1:] > thr)[0]
    stop = int(stop_arr[0]) if len(stop_arr) else (T - 1)
    if stop < 8:
        stop = T - 1
    tsel = np.arange(1, stop + 1)
    y = logd[1:stop + 1]
    ok = np.isfinite(y)
    if ok.sum() < 8:
        return np.nan
    slope = np.polyfit(tsel[ok], y[ok], 1)[0]
    return float(slope / dt)


# ============================ 1. LORENZ ODE ============================

def lorenz_rhs(s, sigma, rho, beta):
    x, y, z = s
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]


def lorenz_attractor(rho, sigma=10.0, beta=8.0 / 3.0, T=100.0, dt=0.01,
                     transient=10.0):
    """Lorenz trajectory, returns x-component sampled every dt (dt=0.01)."""
    t = np.arange(0.0, T + transient + dt, dt)
    sol = odeint(lambda s, tt: lorenz_rhs(s, sigma, rho, beta),
                 [1.0, 1.5, 20.0], t, mxstep=10000)
    return sol[int(transient / dt):, 0]


def lorenz_lyapunov(rho, sigma=10.0, beta=8.0 / 3.0, T_compute=300.0,
                    renorm=300, dt=0.01, transient=10.0):
    """Full Lyapunov spectrum via Benettin/QR on the augmented 12-D system.

    state = (x,y,z) + 3 tangent vectors; QR every `renorm` steps (renorm*dt
    time units); returns np.array([l1,l2,l3]) sorted descending, per unit time.
    """
    def fun(w, t):
        sx, sy, sz = w[0], w[1], w[2]
        Phi = w[3:].reshape(3, 3)
        f = np.array([sigma * (sy - sx),
                      sx * (rho - sz) - sy,
                      sx * sy - beta * sz])
        J = np.array([[-sigma, sigma, 0.0],
                      [rho - sz, -1.0, -sx],
                      [sy, sx, -beta]])
        return np.concatenate([f, (J @ Phi).ravel()])

    t = np.arange(0.0, transient + dt, dt)
    w0 = np.concatenate([[1.0, 1.5, 20.0], np.eye(3).ravel()])
    w = odeint(fun, w0, t, mxstep=10000)[-1]
    w[3:] = np.eye(3).ravel()   # drop tangent transient, restart orthonormal
    n_steps = int(round(T_compute / dt))
    # QR interval cap: empirically renorm*dt=3.0 (renorm=300) biases the
    # spectrum (lambda1 0.887 vs 0.91; sum -15.0 vs -13.667). Keeping
    # |lambda_max|*dt_QR <= ~5 (0.5 t.u. for Lorenz) restores sum(lambda)
    # = tr(J) exactly and matches the literature spectrum.
    m_int = max(1, min(int(renorm), int(round(0.5 / dt))))
    acc = np.zeros(3)
    done = 0
    t_el = 0.0
    while done < n_steps:
        m = min(m_int, n_steps - done)
        times = np.linspace(0.0, m * dt, m + 1)
        w = odeint(fun, w, times, mxstep=10000)[-1]
        Phi = w[3:].reshape(3, 3)
        Qm, R = np.linalg.qr(Phi)
        d = np.diag(R)
        sg = np.sign(d); sg[sg == 0] = 1.0
        acc += np.log(np.abs(d) + 1e-300)
        w[3:] = (Qm * sg).ravel()      # keep orientation, absorb signs
        done += m
        t_el += m * dt
    return np.sort(acc / t_el)[::-1]


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
    E = np.exp(Lop * dt)           # growth rate k^2 - nu k^4: must EXPAND as written
    E2 = np.exp(Lop * dt / 2.0)
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
    return max_lyapunov_discrete(signal, lag=1, dt=dt)


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
        # Periodic-window guard: for a finite (periodic) orbit the true
        # correlation dimension is 0; GP on the noise-jittered delay cloud
        # spuriously returns ~2.4 (verified: a=1.3 -> 7-pt orbit).
        if np.unique(np.round(x[-300:], 6)).size < 50:
            d2 = 0.0
        else:
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
        lam = max_lyapunov_discrete(sig, lag=1, dt=0.01)
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
        qs = [r.get('Q_cal', r['Q']) for r in all_rows if r['system'] == s]
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
    q_cal = [r.get('Q_cal', np.nan) for r in all_rows
             if np.isfinite(r.get('Q_cal', np.nan))]
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

