#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kuramoto_topological_escape_phase2.py
=====================================
PHASE II -- Finite-N Topological Escape & Academy DOSSIER-214 Audit.

Builds directly on the Phase-I mean-field Horizon Escape Law
    t_esc(R0, alpha, K0) ~= (2/(alpha*K0)) * R0**(-alpha)                  (LAW)

Question: how do finite-N fluctuations (N in {64,256,1024}), frequency
disorder sigma_omega, and network topology (All-to-All / Watts-Strogatz
Small-World / Barabasi-Albert Scale-Free) modify t_esc and the universal
prefactor U ?

THEORY (falsifiable, derived by DeepSeek V4 Flash):
-----------------------------------------------------------------------
For a network with (symmetric, zero-diagonal) adjacency A, row-normalised
    W = A / <k>          (so the mean-field all-to-all case is W_ij = 1/(N-1))
the linearised/mean-field-like synchronisation mode is amplified by the
largest eigenvalue lambda_max(W) = lambda_max(A)/<k>.  Hence the reduced
order-parameter dynamics acquires an effective coupling K_eff = K0*lambda_max(W),
so the LAW generalises to

    t_esc(N, topo) ~= U_topo * (2/(alpha*K0)) * R0_eff**(-alpha),
    U_topo = 1 / lambda_max(W) = <k> / lambda_max(A).                    (TOPO LAW)

  * All-to-all :  lambda_max(W)=1  -> U=1     (Phase-I LAW recovered)
  * WS small-world: lambda_max(W) ~ O(1)      -> U ~ 1 (weak shift)
  * BA scale-free : lambda_max(A) ~ <k^2>/<k> -> U < 1 (hubs speed escape)

FINITE-N NOISE FLOOR: in a finite population the *realised* initial
coherence cannot be smaller than the intrinsic fluctuation floor
    R0_eff ~ R0 + c/sqrt(N),      c = O(1).
Hence, as the nominal R0 -> 0, t_esc SATURATES at
    t_esc_floor ~ (2/(alpha*K0)) * (c/sqrt(N))**(-alpha)  ~ N**(alpha/2).
That is the finite-N noise floor whose slope = alpha/2 in log t vs log N.

Everything is vectorised over an ENSEMBLE of independent seeds (axis 0) so
one Python-level step advances all realisations simultaneously; small/none
networks use dense NumPy einsum, larger ones fall back to sparse CSR.

Outputs:
  * kuramoto_topological_escape_phase2.png   (4-panel diagnostic figure)
  * kuramoto_topological_escape_phase2.json  (raw metrics for the dossier)
"""
import json
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')                       # headless
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, issparse

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────
ALPHA        = 1.0            # reflexive exponent (Phase-I centre value)
K0           = 2.0            # base coupling
SIGMA_OMEGA  = 0.5            # default frequency disorder (rad/s)
N_LIST       = [64, 256, 1024]
TOPOS        = ['all_to_all', 'watts_strogatz', 'barabasi_albert']
SEEDS        = 5              # ensemble size
R0_SWEEP     = [0.03, 0.06, 0.12, 0.24]     # nominal initial coherence
SIGMA_SWEEP  = [0.0, 0.5]                    # disorder for the N x topology scan
RC           = 0.9            # escape threshold
DT           = 0.04
MAX_T        = 220.0
RNG_GLOBAL   = 12345

# ──────────────────────────────────────────────────────────────────────
# Topology generators (networkx if available, else self-contained)
# ──────────────────────────────────────────────────────────────────────
def _adj_all_to_all(N, rng):
    W = np.full((N, N), 1.0 / (N - 1))
    np.fill_diagonal(W, 0.0)
    return W

def _adj_watts_strogatz(N, rng, k=6, p=0.15):
    try:
        import networkx as nx
        G = nx.watts_strogatz_graph(N, k, p, seed=int(rng.integers(1 << 30)))
        A = nx.to_numpy_array(G)
    except Exception:                        # pragma: no cover
        A = np.zeros((N, N))
        for i in range(N):
            for j in range(1, k // 2 + 1):
                A[i, (i + j) % N] = 1.0
                A[(i + j) % N, i] = 1.0
        for i in range(N):                   # random rewiring
            for j in range(1, k // 2 + 1):
                if rng.random() < p:
                    a = i
                    b = (i + j) % N
                    if A[a, b]:
                        A[a, b] = A[b, a] = 0.0
                        c = int(rng.integers(0, N))
                        while c == a or A[a, c]:
                            c = int(rng.integers(0, N))
                        A[a, c] = A[c, a] = 1.0
    ks = A.sum(axis=1)
    W = A / max(ks.mean(), 1e-12)
    return W

def _adj_barabasi(N, rng, m=3):
    try:
        import networkx as nx
        G = nx.barabasi_albert_graph(N, m, seed=int(rng.integers(1 << 30)))
        A = nx.to_numpy_array(G)
    except Exception:                        # pragma: no cover
        A = np.zeros((N, N))
        targets = list(range(m + 1))
        for i in range(m + 1):
            for j in range(i + 1, m + 1):
                A[i, j] = A[j, i] = 1.0
        for new in range(m + 1, N):
            deg = A.sum(axis=1)[:new]
            probs = deg / deg.sum()
            chosen = rng.choice(new, size=m, replace=False, p=probs)
            for c in chosen:
                A[new, c] = A[c, new] = 1.0
    ks = A.sum(axis=1)
    W = A / max(ks.mean(), 1e-12)
    return W

TOPO_FN = {
    'all_to_all': _adj_all_to_all,
    'watts_strogatz': _adj_watts_strogatz,
    'barabasi_albert': _adj_barabasi,
}

# ──────────────────────────────────────────────────────────────────────
# Vectorised reflexive Kuramoto with network coupling
#   dtheta_i/dt = omega_i + K0 * R**alpha * sum_j W_ij sin(theta_j - theta_i)
#   R e^{i psi} = (1/N) sum_j sum_batch e^{i theta_j}
# Ensemble state: theta (Seeds, N); omega (Seeds, N); W (N,N).
# ──────────────────────────────────────────────────────────────────────
def _rhs(theta, omega, W, K0, alpha):
    z = np.exp(1j * theta)                        # (S,N)
    R = np.abs(z.mean(axis=1))                    # (S,)
    coef = K0 * R ** alpha                        # (S,)
    # network drive: sum_j W_ij sin(theta_j - theta_i)
    # = Im[ conj(e^{i theta_i}) * sum_j W_ij e^{i theta_j} ]
    if W is None:
        N = theta.shape[1]
        drive = (z.sum(axis=1, keepdims=True) - z) / (N - 1)
    else:
        drive = (W @ z.T).T                       # (S,N)
    net = np.imag(np.conj(z) * drive)             # (S,N)
    return omega + coef[:, None] * net            # (S,N)

def simulate(theta0, omega, W, K0, alpha, dt, max_t, Rc, is_all_to_all=False):
    """RK4, vectorised over ensemble axis. Returns per-seed escape times."""
    S, N = theta0.shape
    t_esc = np.full(S, np.nan)
    theta = theta0.copy()
    n_steps = int(max_t / dt)
    Wsp = None if is_all_to_all else (csr_matrix(W) if (N > 200) else W)
    for step in range(n_steps):
        t = (step + 1) * dt
        k1 = _rhs(theta, omega, Wsp, K0, alpha)
        k2 = _rhs(theta + 0.5 * dt * k1, omega, Wsp, K0, alpha)
        k3 = _rhs(theta + 0.5 * dt * k2, omega, Wsp, K0, alpha)
        k4 = _rhs(theta + dt * k3, omega, Wsp, K0, alpha)
        theta = theta + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        R = np.abs(np.exp(1j * theta).mean(axis=1))
        newly = np.isnan(t_esc) & (R >= Rc)
        t_esc[newly] = t
        if np.all(~np.isnan(t_esc)):
            break
    return t_esc

def make_initial_state(N, S, R0, rng):
    """Von Mises-like wrapped-Gaussian around psi=0 with coherence ~ R0."""
    kappa = 2.0 * R0 / max(1e-9, 1.0 - R0 * R0)   # rough kappa ~ 2R0 for small R0
    kappa = max(kappa, 0.0)
    theta = rng.normal(0.0, 1.0 / np.sqrt(max(kappa, 1e-9)), size=(S, N))
    return np.mod(theta, 2 * np.pi)

# ──────────────────────────────────────────────────────────────────────
# Core scan: N x topology x sigma_omega x R0  (ensemble averaged)
# ──────────────────────────────────────────────────────────────────────
def run_scan():
    rng = np.random.default_rng(RNG_GLOBAL)
    records = []
    for N in N_LIST:
        for topo in TOPOS:
            rng_t = np.random.default_rng(RNG_GLOBAL + 100 * N + hash(topo) % 997)
            W = TOPO_FN[topo](N, rng_t)
            lam_max_W = float(np.max(np.linalg.eigvalsh(0.5 * (W + W.T))))
            U_pred = 1.0 / lam_max_W
            mean_k = float((W * N).sum() / N) if topo != 'all_to_all' else N - 1
            for sigma in SIGMA_SWEEP:
                for R0 in R0_SWEEP:
                    theta0 = make_initial_state(N, SEEDS, R0, rng)
                    omega = rng.normal(0.0, sigma, size=(SEEDS, N))
                    t0 = time.perf_counter()
                    t_esc = simulate(theta0, omega, W, K0, ALPHA, DT, MAX_T, RC, is_all_to_all=(topo == 'all_to_all'))
                    wall = time.perf_counter() - t0
                    R0_real = float(np.mean(np.abs(np.exp(1j * theta0).mean(axis=1))))
                    t_mf = (2.0 / (ALPHA * K0)) * R0_real ** (-ALPHA)
                    t_med = float(np.nanmedian(t_esc))
                    n_esc = int(np.sum(~np.isnan(t_esc)))
                    rec = dict(N=N, topo=topo, sigma=sigma, R0_nominal=R0,
                               R0_real=R0_real, lam_max_W=lam_max_W,
                               U_pred=U_pred, t_esc_med=t_med,
                               t_esc_mf=t_mf,
                               U_meas=(t_med / t_mf if np.isfinite(t_med) and t_mf > 0 else np.nan),
                               n_escaped=n_esc, n_seeds=SEEDS, wall_s=wall)
                    records.append(rec)
                    print(f"N={N:5d} {topo:16s} sig={sigma:.1f} R0={R0:.2f} "
                          f"R0real={R0_real:.3f} t_esc={t_med:8.2f} "
                          f"t_mf={t_mf:8.2f} U_meas={rec['U_meas']:.3f} "
                          f"U_pred={U_pred:.3f} ({wall:.1f}s)")
    return records

# ──────────────────────────────────────────────────────────────────────
# Figure
# ──────────────────────────────────────────────────────────────────────
def make_figure(records):
    import collections
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    cols = {'all_to_all': 'C0', 'watts_strogatz': 'C2', 'barabasi_albert': 'C3'}
    mk = {'all_to_all': 'o', 'watts_strogatz': 's', 'barabasi_albert': '^'}

    # ---- Panel A: finite-N noise floor  (t_esc vs N, fixed R0, sigma=0.5)
    ax = axs[0, 0]
    R0_fix = R0_SWEEP[0]
    for topo in TOPOS:
        xs, ys = [], []
        for N in N_LIST:
            vals = [r['t_esc_med'] for r in records
                    if r['N'] == N and r['topo'] == topo
                    and r['R0_nominal'] == R0_fix and r['sigma'] == 0.5]
            if vals and np.isfinite(vals[0]):
                xs.append(N); ys.append(vals[0])
        ax.plot(xs, ys, mk[topo] + '-', color=cols[topo], label=topo, ms=8)
    # noise-floor slope alpha/2 reference
    Nn = np.array(N_LIST, float)
    ref = (2.0 / (ALPHA * K0)) * (1.0 / np.sqrt(Nn)) ** (-ALPHA)
    ref = ref * (records[0]['t_esc_med'] / ref[0] if ref[0] > 0 else 1)
    ax.plot(Nn, ref, 'k--', lw=1, label=r'floor slope $\alpha/2=0.5$')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('N'); ax.set_ylabel(r'$t_{esc}$ (median)')
    ax.set_title(f'(A) Finite-N noise floor (R0={R0_fix}, $\\sigma_\\omega$=0.5)')
    ax.legend(fontsize=8)

    # ---- Panel B: topological prefactor U (measured vs predicted)
    ax = axs[0, 1]
    for topo in TOPOS:
        xs, ys = [], []
        for N in N_LIST:
            vals = [r['U_meas'] for r in records
                    if r['N'] == N and r['topo'] == topo and r['sigma'] == 0.5]
            if vals and np.isfinite(np.nanmean(vals)):
                xs.append(N); ys.append(np.nanmean(vals))
        ax.plot(xs, ys, mk[topo] + '-', color=cols[topo], label=f'{topo} (meas)', ms=8)
        up = [r['U_pred'] for r in records if r['topo'] == topo][0]
        ax.axhline(up, color=cols[topo], ls=':', lw=1.2,
                   label=f'{topo} $U_{{pred}}$={up:.3f}')
    ax.axhline(1.0, color='k', ls='--', lw=0.8)
    ax.set_xscale('log')
    ax.set_xlabel('N'); ax.set_ylabel(r'$U = t_{esc}/t_{MF}$')
    ax.set_title(r'(B) Topological prefactor $U=<k>/\lambda_{max}(A)$')
    ax.legend(fontsize=7)

    # ---- Panel C: R0 sweep collapse with topology prefactor shift
    ax = axs[1, 0]
    for topo in TOPOS:
        xs, ys = [], []
        for R0 in R0_SWEEP:
            vals = [r['t_esc_med'] for r in records
                    if r['N'] == 1024 and r['topo'] == topo
                    and r['R0_nominal'] == R0 and r['sigma'] == 0.5]
            if vals and np.isfinite(vals[0]):
                xs.append(R0); ys.append(vals[0])
        ax.loglog(xs, ys, mk[topo] + '-', color=cols[topo], label=topo, ms=8)
    R0a = np.array(R0_SWEEP)
    ax.loglog(R0a, (2 / (ALPHA * K0)) * R0a ** (-ALPHA), 'k--', lw=1.2,
              label='Phase-I LAW')
    ax.set_xlabel('nominal $R_0$'); ax.set_ylabel(r'$t_{esc}$')
    ax.set_title('(C) Escape-time law vs $R_0$ (N=1024)')
    ax.legend(fontsize=8)

    # ---- Panel D: disorder sensitivity
    ax = axs[1, 1]
    width = 0.35
    xk = np.arange(len(N_LIST))
    for i, topo in enumerate(TOPOS):
        for s_i, sigma in enumerate(SIGMA_SWEEP):
            vals = []
            for N in N_LIST:
                grouped = [r['t_esc_med'] for r in records
                           if r['N'] == N and r['topo'] == topo and r['sigma'] == sigma]
                vals.append(np.nanmedian(grouped) if grouped else np.nan)
            ax.bar(xk + (i - 1) * width * 0.9, vals, width=width * 0.45,
                   color=cols[topo], alpha=(0.45 if s_i else 0.9),
                   label=f'{topo} $\\sigma$={sigma}')
    ax.set_xticks(xk); ax.set_xticklabels([f'N={n}' for n in N_LIST])
    ax.set_yscale('log'); ax.set_ylabel(r'$t_{esc}$ (median)')
    ax.set_title(r'(D) Disorder $\sigma_\omega$ sensitivity')
    ax.legend(fontsize=6, ncol=2)

    fig.suptitle('PHASE II — Finite-N Topological Escape Law  '
                 r'($t_{esc}\sim U_{topo}\,R_0^{-\alpha}/\alpha K_0$)',
                 fontsize=14, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig('kuramoto_topological_escape_phase2.png', dpi=200, bbox_inches='tight')
    print('Figure saved: kuramoto_topological_escape_phase2.png')
    return fig

# ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    t0 = time.perf_counter()
    print('PHASE II — finite-N topological escape scan')
    print(f'  alpha={ALPHA} K0={K0} N={N_LIST} topos={TOPOS} '
          f'seeds={SEEDS} sigma={SIGMA_SWEEP}')
    records = run_scan()
    total = time.perf_counter() - t0
    print(f'Scan wall clock: {total:.1f}s over {len(records)} configs')

    # fit noise-floor exponent from N-sequence at small R0
    floor_pts = []
    for N in N_LIST:
        vals = [r['t_esc_med'] for r in records
                if r['N'] == N and r['topo'] == 'all_to_all'
                and r['R0_nominal'] == R0_SWEEP[0] and r['sigma'] == 0.5]
        if vals and np.isfinite(vals[0]):
            floor_pts.append((N, vals[0]))
    if len(floor_pts) >= 2:
        a_n = np.array([p[0] for p in floor_pts], float)
        t_n = np.array([p[1] for p in floor_pts], float)
        slope = np.polyfit(np.log(a_n), np.log(t_n), 1)[0]
        print(f'Noise-floor exponent (log t vs log N): {slope:.3f} '
              f'(theory alpha/2={ALPHA/2:.2f})')

    make_figure(records)

    with open('kuramoto_topological_escape_phase2.json', 'w') as f:
        json.dump(records, f, indent=2, default=float)
    print('Data saved: kuramoto_topological_escape_phase2.json')
    print('=' * 60)
    print('SUMMARY')
    print('=' * 60)
    for topo in TOPOS:
        us = [r['U_meas'] for r in records if r['topo'] == topo]
        up = [r['U_pred'] for r in records if r['topo'] == topo][0]
        print(f'  {topo:16s} U_meas={np.nanmedian(us):.3f}  U_pred={up:.3f}')
    print('=' * 60)
